# agents/planner.py
import os
from langchain_ollama import ChatOllama
from crewai import Agent

# Kill OpenAI completely
os.environ.pop("OPENAI_API_KEY", None)
os.environ.pop("OPENAI_BASE_URL", None)

# Direct Ollama LLM
llm = ChatOllama(
    model="qwen2.5:14b-instruct-q6_K",
    base_url="http://localhost:11434",
    temperature=0.3
)

raise NotImplementedError("This module is deprecated. Use dep_planner.py instead.")

# Bypass CrewAI's broken LLM routing with a safe wrapper
class LocalLLM:
    def __init__(self, llm):
        self.llm = llm
    def __call__(self, messages, **kwargs):
        return self.llm.invoke(messages)
    def bind(self, **kwargs):
        return self

safe_llm = LocalLLM(llm)

planner = Agent(
    role="Homework Planner",
    goal="Create detailed, realistic daily study plans from all available homework",
    backstory="You are an expert academic coach who breaks down assignments into manageable daily tasks.",
    llm=safe_llm,
    allow_delegation=False,
    verbose=True,
    memory=False
)