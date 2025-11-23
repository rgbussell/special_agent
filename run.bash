# 1. Start Ollama (leave this terminal open)
ollama serve

# 2. In another terminal
cd "${HOME}/projects/special_agent/"
source venv/bin/activate    # Windows: venv\Scripts\activate
chainlit run ui/app.py -w   # -w = auto-reload