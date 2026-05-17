def check_hallucination(corpus_text: str, quoted_evidence: str) -> bool:
    """Returns True if evidence is verified in corpus."""
    return quoted_evidence in corpus_text
