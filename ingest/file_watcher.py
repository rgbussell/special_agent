import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
import pytesseract

class HomeworkHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}:
            print(f"New homework detected: {path.name}")
            text = extract_text(path)
            from agents.knowledge import add_documents
            add_documents([text], [{"source": path.name, "type": "homework"}])
            # Trigger UI update
            with open("data/latest_homework.txt", "w") as f:
                f.write(text)

def extract_text(path: Path) -> str:
    if path.suffix == ".pdf":
        doc = fitz.open(path)
        return " ".join(page.get_text() for page in doc)
    elif path.suffix == ".docx":
        return " ".join(p.text for p in Document(path).paragraphs)
    elif path.suffix == ".txt":
        return path.read_text()
    elif path.suffix in {".png", ".jpg", ".jpeg"}:
        return pytesseract.image_to_string(Image.open(path))
    return ""