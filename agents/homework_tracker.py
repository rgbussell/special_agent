# agents/homework_tracker.py
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from datetime import datetime
from typing import List, Dict

llm = ChatOllama(
    model="qwen2.5:14b-instruct-q6_K",
    base_url="http://localhost:11434",
    temperature=0.2
)

# Step 1: Extract structured homework info from every document
extractor_prompt = ChatPromptTemplate.from_template("""
You are an expert homework parser. For the following assignment text, extract:

- class_name: the subject/class (e.g. "Algebra II", "AP Physics", "English 12")
- assignment_title: short description
- due_date: the exact due date in YYYY-MM-DD format (guess the year if missing, assume current school year)
- raw_due_text: the original text that mentioned the due date

If no due date → return null for due_date.
If no clear class → use "General" or "Unknown".

Return valid JSON only.

Text:
{text}
""")

parser = JsonOutputParser()

extract_chain = extractor_prompt | llm | parser

def extract_homeworks_from_all_docs(docs) -> List[Dict]:
    results = []
    for doc in docs:
        text = doc.page_content
        try:
            raw = extract_chain.invoke({"text": text})
            data = raw if isinstance(raw, dict) else raw.get("parsed", {})
            if data.get("due_date") or data.get("assignment_title"):
                data["source"] = doc.metadata.get("source", "unknown")
                results.append(data)
        except Exception as e:
            print(f"Failed to parse a document: {e}")
            continue
    return results

# Step 2: Final pretty response chain
response_prompt = ChatPromptTemplate.from_template("""
You are a friendly homework tracker.

Here is the structured list of all homework with due dates found:

{structured_homework}

User request: {user_input}

Instructions:
- If the user mentions a specific class/subject → show only that class
- If the user mentions a time range (e.g. "this week", "December", "next 7 days", "before Christmas", "past due") → filter accordingly
- If no filter → show everything, grouped by class, then sorted by due date
- Today is {today}
- Use clean markdown with emojis
- If nothing is due in the requested range → say so clearly

Respond naturally and beautifully.
""")

response_chain = response_prompt | llm

def build_homework_report(docs, user_input: str):
    structured = extract_homeworks_from_all_docs(docs)
    
    # Simple post-filtering for dates the LLM sometimes misses
    today = datetime.now().strftime("%Y-%m-%d")
    report = response_chain.invoke({
        "structured_homework": structured,
        "user_input": user_input.lower(),
        "today": today
    })
    return report.content