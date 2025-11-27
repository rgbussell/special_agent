from email.mime import text
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import fitz  # PyMuPDF for PDF
from docx import Document  # DOCX
from PIL import Image
import pytesseract
from agents.dep_knowledge import add_documents
import logging

class HomeworkHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}:
            logging.info(f"New file detected: {path.name}")
            text = self.extract_text(path)

            if text.strip():
                logging.info(f"Extracted text length: {len(text)} characters")
                logging.info(f"First 500 chars: {text[:500]!r}")
                logging.info(f"Contains 'Book Thief': {'Book Thief' in text}")
                logging.info(f"Contains 'Socratic': {'Socratic' in text}")
                logging.info("-" * 80)
 
                add_documents([text], [{"source": path.name, "type": "homework"}])

                # Optional: Trigger UI update via file flag
                with open("data/latest_homework.txt", "w") as f:
                    f.write(text)
            else:
                logging.warning(f"No text extracted from {path.name}")

    def extract_text(self, path: Path) -> str:
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