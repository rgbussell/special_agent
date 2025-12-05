## memory

## LLMs

| Area | Details |
|---|---|
| Workflow | langchain |
| Local LLMs | Llama 3 |
| Cloud / Interfaces | Grok or OpenAI interfaces for improved performance |

## Multi-agent repo architecture

homework-agent/<br>
├── main.py                 # Launch file (run this) <br>
├── agents/<br>
│   ├── planner.py<br>
│   ├── tutor.py<br>
│   └── knowledge.py<br>
├── ingest/<br>
│   ├── file_watcher.py<br>
│   └── email_checker.py<br>
├── ui/<br>
│   └── app.py              # Chainlit UI<br>
├── data/<br>
│   ├── inbox/              # ← DROP HOMEWORK FILES HERE<br>
│   └── knowledge/          # ← Put your notes, syllabus, etc.<br>
├── .env                    # Your secrets<br>
└── requirements.txt<br>

## Local bias

| Goal | Notes |
|---|---|
| Run locally when feasible | Keep LLMs and data local to maximize security and reduce costs; target: 12 GB VRAM GPU |

## Build components and resource estimates

| Component | Best Tool (2025) | VRAM Usage (approx) | Notes |
|---|---:|---:|---|
| LLM Backend | Ollama + LM Studio or llama.cpp | 7–10 GB | Easiest and fastest |
| Main Reasoning Model | Llama 3.1 70B (Q4/Q5) or Llama 3.2 90B (Q4) | 8–10 GB | Best quality/speed balance on 12 GB |
| Alternative (faster) | Qwen2.5 72B (Q4_K_M) or DeepSeek-R1 70B | ~9 GB | Often better at math/reasoning |
| Alternative (<32GB RAM) | Qwen2.5 14 (Q6_K) | ~9 GB VRAM | For RAM constrained system |
| Small/fast tutor models | Llama 3.2 3B or Phi‑4 14B | 2–6 GB | Quick subject-specific tutors |
| Vector Database | ChromaDB (local) | < 1 GB | Runs on disk |
| File/Directory Watcher | watchdog (Python) | negligible | Local |
| Email Ingestion | IMAP + Python (local script) | negligible | Local |
| Multi-Agent Framework | LangChain Workflows | — | Fully local |
| UI | Chainlit | < 1 GB | Runs locally in browser |

## model consistent with 12 GB VRAM

| Model | Quantization | VRAM Needed | Reasoning Quality | Speed | Download Command (Ollama) |
|---|---|---|---|---|---|
| llama3.1:70b-q4_K_M | Q4 | ~9.5 GB | Excellent | Good | ollama pull llama3.1:70b-q4_K_M |
| qwen2.5:72b-instruct-q4_K_M | Q4 | ~9.8 GB | Top-tier (often beats 70B Llama) | Very good | ollama pull qwen2.5:72b-instruct-q4_K_M |
| deepseek-r1:70b-q4_K_M | Q4 | ~9.5 GB | Exceptional at homework/planning | Fast | Available on Ollama library |
| llama3.2:3b-instruct | Q8 | ~3 GB | Great for fast tutors | Very fast | ollama pull llama3.2:3b |

## tutor model choice
Want to use llama3.2:3b-instruct as this was tuned for following user prompts, dialogs and has fewer hallucinations.
However, this is not currently released, so evaluating these moodel: 
qwen2.5:14b-instruct-q6_K
qwen2.5:32b-instruct-q4_K_M

Model consideration
* size, of course
* speed of inference (minor consideration)
* context length
* performance as math and language instructor

# UI choices
streamlit versus chainlit: In this project I opt for chainlit because the llm/chat support<br>
is natively built which may help make the UI more conversational. In contrast streamlit <br>
would be more suitable for data visualization applications.

# Shared data storage
chromadb to be used as a vector database for storing shared information

# Security considerations
API will and secrets will be handled using .dotenv approach

# Agents
* knowledge
* homework tracker
* file watcher
* email watcher