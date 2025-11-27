from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os
load_dotenv()

def check_emails():
    emails = []
    try:
        with MailBox('imap.gmail.com').login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"), 'INBOX') as mailbox:
            for msg in mailbox.fetch(AND(seen=False, subject='homework')):
                body = msg.text or msg.html or ''
                emails.append(f"Subject: {msg.subject}\nFrom: {msg.from_}\nBody: {body[:2000]}...")
        print(f"Checked {len(emails)} emails.")
    except Exception as e:
        print(f"Email check failed: {e}")
    return emails