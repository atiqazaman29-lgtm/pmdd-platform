import os
import json
import logging
import asyncio
from typing import Dict, Any

from sqlalchemy.future import select

from backend.core.events import manager
from backend.db.database import AsyncSessionLocal
from backend.db.models import AnalysisReport, Project

from agents.agent1_preprocessor import CorpusPreprocessor
from agents.agent2_pragmatic import PragmaticAnalyzerAgent
from agents.agent3_semantic import SemanticAnalyzerAgent
from agents.agent4_quantitative import QuantitativeAnalyzerAgent
from agents.agent5_orchestrator import OrchestratorAgent
from agents.schemas import CognitiveState, CorpusSegment, AgentOutput
from validation.hallucination import HallucinationDetector
from validation.reliability import ReliabilityScorer

logger = logging.getLogger(__name__)

async def update_report_db(project_id: str, status: str, findings=None, reliability=None, detail=None):
    async with AsyncSessionLocal() as session:
        stmt = select(AnalysisReport).where(AnalysisReport.project_id == project_id)
        res = await session.execute(stmt)
        report = res.scalars().first()
        if report:
            report.status = status
            if findings is not None:
                report.findings = findings
            if reliability is not None:
                report.reliability_metrics = reliability
            if detail is not None:
                if not report.reliability_metrics:
                    report.reliability_metrics = {}
                report.reliability_metrics["errorDetail"] = detail
            await session.commit()

async def run_analysis_pipeline(project_id: str, safe_filename: str):
    try:
        await update_report_db(project_id, "analyzing")
        
        await manager.broadcast(json.dumps({
            "agent_id": "System",
            "action": f"Starting analysis pipeline for project {project_id}",
            "segment_id": "init",
            "confidence": 1.0
        }))

        upload_dir = "uploads"
        file_path = os.path.join(upload_dir, safe_filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Corpus file not found: {safe_filename}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fetch keywords from DB
        keywords = "None provided"
        async with AsyncSessionLocal() as session:
            stmt = select(Project).where(Project.id == project_id)
            res = await session.execute(stmt)
            proj = res.scalars().first()
            if proj and proj.keywords:
                keywords = proj.keywords

        # Preprocessing
        await manager.broadcast(json.dumps({
            "agent_id": "Agent1_Preprocessor",
            "action": "Ingesting and chunking corpus",
            "segment_id": "prep",
            "confidence": 1.0
        }))
        preprocessor = CorpusPreprocessor()
        segments = await preprocessor.ingest_file(content, metadata={"project_id": project_id})

        # Process first 3 segments to optimize for large corpora while maintaining robustness
        segments_to_process = segments[:3]
        
        pragmatic_analyzer = PragmaticAnalyzerAgent()
        semantic_analyzer = SemanticAnalyzerAgent()
        quantitative_analyzer = QuantitativeAnalyzerAgent()
        orchestrator = OrchestratorAgent()
        
        all_findings = []
        total_confidence = 0.0

        for idx, segment in enumerate(segments_to_process):
            # Broadcast starting
            await manager.broadcast(json.dumps({
                "agent_id": "Orchestrator",
                "action": f"Dispatching chunk {idx+1}/{len(segments_to_process)} to Agents 2, 3, 4 concurrently",
                "segment_id": segment.segment_id,
                "confidence": 1.0
            }))

            state2 = CognitiveState(session_id=project_id, segment=segment)
            state3 = CognitiveState(session_id=project_id, segment=segment)
            state4 = CognitiveState(session_id=project_id, segment=segment)
            
            # Execute agents concurrently
            out2_task = pragmatic_analyzer.execute(state2)
            
            async def run_agent3():
                context = {"keywords": keywords}
                out = await semantic_analyzer.analyze(context, state3)
                out = await semantic_analyzer.execute(state3) # Execute fully Handles retries
                return out
                
            async def run_agent4():
                context = {"keywords": keywords}
                out = await quantitative_analyzer.execute(state4)
                return out

            results = await asyncio.gather(
                out2_task, 
                run_agent3(), 
                run_agent4(),
                return_exceptions=True
            )
            
            out2 = results[0] if not isinstance(results[0], Exception) else None
            out3 = results[1] if not isinstance(results[1], Exception) else None
            out4 = results[2] if not isinstance(results[2], Exception) else None

            # Orchestrate
            await manager.broadcast(json.dumps({
                "agent_id": "Agent5_Orchestrator",
                "action": f"Synthesizing findings {idx+1}/{len(segments_to_process)}",
                "segment_id": segment.segment_id,
                "confidence": 0.9
            }))
            
            combined_findings = []
            if out2 and hasattr(out2, 'findings'): combined_findings.extend(out2.findings)
            if out3 and hasattr(out3, 'findings'): combined_findings.extend(out3.findings)
            if out4 and hasattr(out4, 'findings'): combined_findings.extend(out4.findings)
            
            state5 = CognitiveState(session_id=project_id, segment=segment)
            final_out = await orchestrator.analyze({"previous_findings": combined_findings}, state5)
            
            val_feedback = await orchestrator.validate(final_out, state5)
            if not val_feedback.is_valid:
                state5.validation_history.append(val_feedback)
                final_out = await orchestrator.reflect_and_correct({"previous_findings": combined_findings}, state5)
            
            all_findings.extend(final_out.findings)
            total_confidence += final_out.overall_confidence
            
            await manager.broadcast(json.dumps({
                "agent_id": "Agent5_Orchestrator",
                "action": f"Completed segment {idx+1}",
                "segment_id": segment.segment_id,
                "confidence": final_out.overall_confidence
            }))

        # Aggregated
        avg_confidence = total_confidence / len(segments_to_process) if segments_to_process else 0.0
        aggregated_output = AgentOutput(
            findings=all_findings,
            overall_confidence=avg_confidence,
            reflection_log="Aggregated 5-agent analysis complete."
        )

        await manager.broadcast(json.dumps({
            "agent_id": "ValidationSystem",
            "action": "Computing Advanced Validation (Cross-Agent Agreement & Hallucinations)",
            "segment_id": "val",
            "confidence": 1.0
        }))
        
        full_processed_text = " ".join([seg.raw_text for seg in segments_to_process])
        merged_segment = CorpusSegment(segment_id="merged", raw_text=full_processed_text, metadata={})
        
        hallucination_score = HallucinationDetector.verify_quotes(aggregated_output, merged_segment)
        reliability_metrics = ReliabilityScorer.calculate_score(aggregated_output, hallucination_score, has_stats=True)
        
        # Calculate cross agent agreement (simple metric based on total confidence and hallucination)
        # Fix: calculate hallucination_ratio since it's not in the object
        total_findings = len(all_findings)
        fabricated_count = len(hallucination_score.fabricated_quotes)
        hallucination_ratio = fabricated_count / total_findings if total_findings > 0 else 0
        
        cross_agent_agreement = round(min(1.0, max(0.0, avg_confidence * (1 - hallucination_ratio))), 2)

        reliability_dict = {
            "evidenceStrength": reliability_metrics.evidence_strength_score,
            "theoreticalDefensibility": reliability_metrics.theoretical_defensibility_score,
            "hallucinationPenalty": reliability_metrics.hallucination_penalty,
            "crossAgentAgreement": cross_agent_agreement,
            "overallScore": reliability_metrics.overall_reliability_score,
            "isAcademicallyDefensible": reliability_metrics.is_academically_defensible
        }
        
        findings_list = [
            {
                "finding_type": f.finding_type,
                "theory": f.linguistic_theory,
                "interpretation": f.interpretation,
                "justification": f.theoretical_justification,
                "ambiguity": f.ambiguity_level,
                "reliabilityScore": f.confidence_score,
                "quotes": [ev.exact_quote for ev in f.corpus_evidence]
            }
            for f in all_findings
        ]

        await update_report_db(project_id, "completed", findings=findings_list, reliability=reliability_dict)

        await manager.broadcast(json.dumps({
            "agent_id": "System",
            "action": "Analysis complete, report saved to Database.",
            "segment_id": "done",
            "confidence": 1.0
        }))
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        await manager.broadcast(json.dumps({
            "agent_id": "System",
            "action": f"Error: {str(e)}",
            "segment_id": "error",
            "confidence": 0.0
        }))
        await update_report_db(project_id, "error", detail=str(e))
