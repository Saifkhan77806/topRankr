def start_gmail_watch(service):
    request = {
        "topicName":
        "projects/toprankr/topics/gmail-topic"
    }

    response = service.users().watch(
        userId="me",
        body=request
    ).execute()

    print(response)
