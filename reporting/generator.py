import json
from typing import List, Dict, Any
from reporting.schemas import FinalResearchReport, ReportSection, ReportCitation
from reporting.synthesis import CrossAgentSynthesizer
from reporting.visualizations import VisualizationEngine

class ReportEngine:
    """Assembles the final academic report from raw agent states."""
    
    def __init__(self):
        self.synthesizer = CrossAgentSynthesizer()
        self.viz_engine = VisualizationEngine()
        
    async def generate_report(self, corpus_id: str, agent_states: List[Dict[str, Any]]) -> FinalResearchReport:
        # Synthesize findings
        synthesis = await self.synthesizer.synthesize(agent_states)
        
        # Generate Visualizations
        viz_paths = self.viz_engine.generate_all(synthesis)
        
        # Build sections
        sections = [
            ReportSection(
                title="Executive Summary",
                content=synthesis["summary"],
                ambiguity_warnings=synthesis["ambiguities"]
            ),
            ReportSection(
                title="Pragmatic Drift Analysis",
                content=synthesis["pragmatic_drift_text"],
                citations=synthesis["citations"],
                visualizations=[viz_paths.get("heatmap")] if viz_paths.get("heatmap") else []
            )
        ]
        
        return FinalResearchReport(
            corpus_id=corpus_id,
            title=f"Linguistic Analysis Report: Corpus {corpus_id}",
            executive_summary=synthesis["summary"],
            sections=sections,
            overall_reliability=synthesis["average_reliability"]
        )
