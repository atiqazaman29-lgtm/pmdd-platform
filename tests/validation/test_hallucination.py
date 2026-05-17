import pytest
from validation.hallucination import HallucinationDetector
from agents.schemas import AgentOutput, CorpusSegment, LinguisticFinding, EvidenceReference

def test_hallucination_detector_pass():
    segment = CorpusSegment(segment_id="1", raw_text="The quick brown fox jumps.")
    finding = LinguisticFinding(
        finding_type="Test",
        linguistic_theory="Test Theory",
        interpretation="Test",
        theoretical_justification="Test",
        confidence_score=0.9,
        ambiguity_level="Low",
        corpus_evidence=[EvidenceReference(segment_id="1", exact_quote="quick brown fox")]
    )
    output = AgentOutput(findings=[finding], overall_confidence=0.9, reflection_log="")
    
    score = HallucinationDetector.verify_quotes(output, segment)
    assert not score.is_hallucinated

def test_hallucination_detector_fail():
    segment = CorpusSegment(segment_id="1", raw_text="The quick brown fox jumps.")
    finding = LinguisticFinding(
        finding_type="Test",
        linguistic_theory="Test Theory",
        interpretation="Test",
        theoretical_justification="Test",
        confidence_score=0.9,
        ambiguity_level="Low",
        corpus_evidence=[EvidenceReference(segment_id="1", exact_quote="lazy dog")]
    )
    output = AgentOutput(findings=[finding], overall_confidence=0.9, reflection_log="")
    
    score = HallucinationDetector.verify_quotes(output, segment)
    assert score.is_hallucinated
    assert "lazy dog" in score.fabricated_quotes
