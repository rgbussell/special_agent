from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os
load_dotenv()

def check_emails():
    emails = []
    try:
        with MailBox('imap.gmail.com').login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"), 'INBOX') as mailbox:
            # Use 'subject' for partial match (contains 'homework') — works in all versions
            for msg in mailbox.fetch(AND(seen=False, subject='homework')):  # Or add OR for 'assignment'
                body = msg.text or msg.html or ''
                emails.append(f"Email Subject: {msg.subject}\nFrom: {msg.from_}\n{body[:2000]}...")  # Truncate if too long
        print(f"Successfully checked {len(emails)} emails.")  # Optional: Log success
    except Exception as e:
        print(f"Email check failed (skipping): {e}")  # Graceful fallback
        emails = []  # Don't crash the app
    return emails