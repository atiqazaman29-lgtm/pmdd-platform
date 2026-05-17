from validation.reliability import ReliabilityScorer
from validation.schemas import HallucinationScore
from agents.schemas import AgentOutput, LinguisticFinding, EvidenceReference

def test_reliability_scorer():
    finding = LinguisticFinding(
        finding_type="Test", linguistic_theory="Test Theory", interpretation="Test",
        theoretical_justification="Test", confidence_score=0.9, ambiguity_level="Low",
        corpus_evidence=[
            EvidenceReference(segment_id="1", exact_quote="A"),
            EvidenceReference(segment_id="1", exact_quote="B"),
            EvidenceReference(segment_id="1", exact_quote="C")
        ]
    )
    output = AgentOutput(findings=[finding], overall_confidence=0.9, reflection_log="")
    halluc = HallucinationScore(is_hallucinated=False)
    
    metrics = ReliabilityScorer.calculate_score(output, halluc, has_stats=True)
    assert metrics.is_academically_defensible
    assert metrics.overall_reliability_score > 0.7
