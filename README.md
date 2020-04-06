# ispmon

A Speetest monitor with the ability to send email reports via Mialgun REST api. 

## Requirements

1. docker and docker-compose installed
2. Mailgun account and API key

## Quickstart

1. Navigate to this folder in terminal.
2. Copy `docker-compose-sample.yaml` and save as `docker-compose.yaml`.
3. Edit `docker-compose.yaml` in text editor to include reuqired variables. Save. 
4. To run, run:

    `docker-compose run`

## Required environemnt varibales

| Variable  | Description  |
|---|---|
| MAILGUN_API_KEY | API key provided by Mailgun. |
| MAILGUN_DOMAIN | Domain name configured in Mailgun for sending emails using API key. E.g mail.mydomain.com |
| MAILGUN_FROM_EMAIL | Email address to be set as sender for email reports. E.g. mailer@mail.mydomain.com |
| MAILGUN_FROM_NAME | Name to be set as sender for email reports. E.g. Mailer |
| RECIPIENT_EMAIL | Email address of the person recieving the report E.g. user@domain.com |