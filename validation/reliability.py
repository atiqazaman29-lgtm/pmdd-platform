from agents.schemas import AgentOutput
from validation.schemas import ReliabilityMetrics, HallucinationScore

class ReliabilityScorer:
    """Computes the final scientific reliability of an analysis."""
    
    @staticmethod
    def calculate_score(output: AgentOutput, hallucination: HallucinationScore, has_stats: bool) -> ReliabilityMetrics:
        # Base scores
        evidence_strength = sum([len(f.corpus_evidence) for f in output.findings]) * 0.2
        evidence_strength = min(1.0, evidence_strength)
        
        theory_score = sum([f.confidence_score for f in output.findings]) / len(output.findings) if output.findings else 0.0
        
        stats_score = 1.0 if has_stats else 0.0
        halluc_penalty = 0.5 if hallucination.is_hallucinated else 0.0
        
        # Weighted Final
        overall = (evidence_strength * 0.4) + (theory_score * 0.4) + (stats_score * 0.2) - halluc_penalty
        overall = max(0.0, min(1.0, overall))
        
        return ReliabilityMetrics(
            evidence_strength_score=evidence_strength,
            theoretical_defensibility_score=theory_score,
            statistical_support_score=stats_score,
            hallucination_penalty=halluc_penalty,
            overall_reliability_score=overall,
            is_academically_defensible=overall >= 0.75
        )
