from typing import List
from agents.schemas import AgentOutput
from validation.schemas import ContradictionReport
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class ContradictionAnalyzer:
    """Detects logical contradictions between multiple findings on the same segment."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        
    async def analyze(self, output: AgentOutput) -> ContradictionReport:
        if len(output.findings) <= 1:
            return ContradictionReport(has_contradiction=False)
            
        # Fast fail logic: If ambiguity is explicitly declared, it's not a hidden contradiction
        ambiguities = [f for f in output.findings if f.ambiguity_level in ["Medium", "High"]]
        if len(ambiguities) == len(output.findings):
            return ContradictionReport(has_contradiction=False)
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a logical consistency checker. Analyze the following linguistic findings. Do they logically contradict each other without explicitly acknowledging the ambiguity? Return a JSON object with keys: has_contradiction (bool), conflicting_findings (list of finding types), resolution_suggestion (string)."),
            ("human", "{findings}")
        ])
        
        chain = prompt | self.llm.with_structured_output(ContradictionReport)
        return await chain.ainvoke({"findings": output.model_dump_json()})
