import os.path
import base64
import uuid

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.workers.resume_tasks import (
    process_candidate_email
)



UPLOAD_DIR = "app/uploads/resumes"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]


def get_gmail_service():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    r"F:\TopRankr\TopRankrBackend\app\services\client_secret_654131460148-pp0287v54mul82g5v637o8nq9bthb6fp.apps.googleusercontent.com.json",
                    SCOPES
                    )

            creds = flow.run_local_server(
                port=8080
            )

        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


def check_candidate_emails():

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread has:attachment filename:pdf",
        maxResults=10
    ).execute()

    messages = results.get(
        "messages",
        []
    )

    print(
        f"Found {len(messages)} emails"
    )



    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"]
        ).execute()

        headers = msg["payload"].get(
            "headers",
            []
        )

        sender = ""
        subject = ""

        for header in headers:

            if header["name"] == "From":
                sender = header["value"]

            if header["name"] == "Subject":
                subject = header["value"]

        attachments = []

        parts = msg["payload"].get(
            "parts",
            []
        )

        for part in parts:

            filename = part.get(
                "filename",
                ""
            )

            if filename:
                attachment_id = part["body"].get(
                    "attachmentId"
                )
                if attachment_id:  
                    attachment = (
                        service.users().messages().attachments().get(
                            userId="me",
                            messageId=message["id"],
                            id=attachment_id
                        )
                        .execute()
                    )
                    
                    data = attachment["data"]

                    file_data = base64.urlsafe_b64decode(
                        data.encode("UTF-8")
                    )
                    
                    unique_name = (
                        f"{uuid.uuid4()}_{filename}"
                    )
    
                    filepath = os.path.join(
                        UPLOAD_DIR,
                        unique_name
                    )

                    with open(filepath, "wb") as f:
                        f.write(file_data)

                    attachments.append(
                        filepath
                    )

        email = {
            "from": sender,
            "subject": subject,
            "attachments": attachments
        }

        print("\n========== EMAIL ==========")
        print("FROM:")
        print(sender)

        print("\nSUBJECT:")
        print(subject)

        print("\nATTACHMENTS:")
        print(attachments)

        print("===========================\n")

        process_candidate_email.delay(
            email
        )

        service.users().messages().modify(
            userId="me",
            id=message["id"],
            body={
                "removeLabelIds": [
                    "UNREAD"
                ]
            }
        ).execute()