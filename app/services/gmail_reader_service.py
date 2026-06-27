from googleapiclient.discovery import build

def get_latest_candidate_email(service):
    results = service.users().messages().list(
        userId="me",
        maxResults=1,
        q="is:unread has:attachment"
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        return None

    message = service.users().messages().get(
        userId="me",
        id=messages[0]["id"]
    ).execute()

    print("email message:-\n")
    print(message)

    return {
        "from": "candidate@gmail.com",
        "subject": "Application for AI Engineer",
        "attachments": [
            "resume.pdf"
        ]
    }
