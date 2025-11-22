from agents.summarizer import SummarizerAgent
from agents.test_generator import TestGeneratorAgent
from agents.langchain_wrapper import LangChainRAG


class InternTAAgentsManager:
    def __init__(self, api_key: str):
        self.text = ""
        self.summarizer = SummarizerAgent(api_key)
        self.testgen = TestGeneratorAgent(api_key)
        self.rag = LangChainRAG(api_key)

    def load_material(self, text: str):
        self.text = text
        self.rag.load_text(text)

    def run_rag(self, query: str):
        return self.rag.run(query)

    def run_summary(self, query: str):
        return self.summarizer.summarize(self.text)

    def generate_mcq(self):
        if not self.text:
            return "No material loaded", ["Please upload material first"], "A", "No explanation available"
        return self.testgen.generate_single_mcq(self.text)