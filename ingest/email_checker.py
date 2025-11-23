from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os
load_dotenv()

def check_emails():
    emails = []
    with MailBox('imap.gmail.com').login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"), 'INBOX') as mailbox:
        for msg in mailbox.fetch(AND(seen=False, subject_part='homework')):  # Or 'assignment'
            body = msg.text or msg.html or ''
            emails.append(f"Email Subject: {msg.subject}\nFrom: {msg.from_}\n{body[:2000]}...")  # Truncate if too long
    return emails