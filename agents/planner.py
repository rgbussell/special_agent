from crewai import Agent
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:14b-instruct-q6_K", temperature=0.3)

planner = Agent(
    role="Homework Planner",
    goal="Create detailed, realistic daily study plans from assignments",
    backstory="You are an expert academic coach who breaks down homework into manageable steps.",
    llm=llm,
    allow_delegation=False,
    verbose=True
)