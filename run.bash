cd ~/projects/special_agent
source venv/bin/activate
mkdir -p data/inbox data/vector_db
PYTHONPATH=. chainlit run ui/app.py -w