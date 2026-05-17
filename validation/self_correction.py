from agents.schemas import AgentOutput, ValidationFeedback
from validation.schemas import ReliabilityMetrics

class SelfCorrectionEngine:
    """Orchestrates the feedback loop when validation fails."""
    
    @staticmethod
    def generate_feedback(output: AgentOutput, reliability: ReliabilityMetrics) -> ValidationFeedback:
        errors = []
        if not reliability.is_academically_defensible:
            errors.append(f"Reliability score {reliability.overall_reliability_score} is below academic threshold (0.75).")
            
        if reliability.hallucination_penalty > 0:
            errors.append("CRITICAL: Fabricated corpus evidence detected. Ensure all quotes match the raw text exactly.")
            
        if reliability.evidence_strength_score < 0.5:
            errors.append("Evidence strength is too low. Include more verbatim quotes.")
            
        return ValidationFeedback(
            is_valid=len(errors) == 0,
            errors=errors,
            suggested_correction=" | ".join(errors) if errors else None
        )
