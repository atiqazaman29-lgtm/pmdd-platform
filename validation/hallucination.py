from typing import List
from agents.schemas import AgentOutput, CorpusSegment
from validation.schemas import HallucinationScore
import re

class HallucinationDetector:
    """Strictly verifies corpus grounding to prevent LLM hallucination."""
    
    @staticmethod
    def verify_quotes(output: AgentOutput, segment: CorpusSegment) -> HallucinationScore:
        fabricated = []
        raw_text_normalized = " ".join(segment.raw_text.split())
        
        for finding in output.findings:
            for ev in finding.corpus_evidence:
                quote_normalized = " ".join(ev.exact_quote.split())
                if quote_normalized not in raw_text_normalized:
                    # Allow minor punctuation drift, but fail on word mismatch
                    clean_quote = re.sub(r'[^\w\s]', '', quote_normalized).strip()
                    clean_raw = re.sub(r'[^\w\s]', '', raw_text_normalized)
                    if clean_quote not in clean_raw:
                        fabricated.append(ev.exact_quote)
                        
        return HallucinationScore(
            is_hallucinated=len(fabricated) > 0,
            fabricated_quotes=fabricated
        )
