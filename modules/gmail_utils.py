"""Module to send automatic emails with Gmail.
"""

# standard imports
import argparse
from pathlib import Path
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# third party imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def total_size(files_list):
    """
    Get total size of given list of files.

    Parameters
    ----------
    files_list : [Path, ...]
    """
    size = 0
    for f in files_list:
        size += f.stat().st_size
    return size


def authenticate_google_oauth2(credentials_file, token_file):
    """Authenticate to Google API using OAuth2.

    Parameters
    ----------
    credentials_file : Path
    token_file : Path

    Returns
    -------
    credentials : Credentials
    """
    credentials = None

    # read credentials from token if existing
    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(token_file, SCOPES)

    # request new token if no (valid) credentials available
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            credentials = flow.run_local_server()

        # save credentials for next run
        with open(token_file, "w") as token:
            token.write(credentials.to_json())

    return credentials


def send_mail(
    subject, contents, credentials, sender, recipients, cc=[], bcc=[], attachments=[], logger=None
):
    """
    Send email using Gmail API.

    Parameters
    ----------
    subject : str
    contents : str
    credentials : Credentials
    sender : str
    recipients : [str, ...]
    cc : [str, ...]
    bcc : [str, ...]
    attachments [Path, ...]
        list of files to attach
    logger : logging.Logger or None
    """

    try:

        # create message
        message = MIMEMultipart()

        # adding subject, recipients, CC, and BCC
        message["Subject"] = subject
        message["To"] = ",".join(recipients)
        message["CC"] = ",".join(cc)
        message["BCC"] = ",".join(bcc)

        # add attachments
        attachment_size = total_size(attachments)
        if attachment_size > 10000000:  # case of oversize attachment
            contents += "\nOversized attachment."
        else:
            for attachment in attachments:
                piece = open(attachment, "rb")  # opening report file
                part = MIMEBase("application", "octet-stream")  # encoding attachment in Base64
                part.set_payload((piece).read())  # reading report file in attachment
                encoders.encode_base64(part)  # encoding attachment in Base64
                part.add_header(
                    "Content-Disposition", "piece; filename= {}".format(attachment.name)
                )
                message.attach(part)

        # add contents
        message.attach(MIMEText(contents.encode("utf-8"), "plain", "utf-8"))

        # encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # send message
        create_message = {"raw": encoded_message}
        gmail_service = build("gmail", "v1", credentials=credentials)
        send_message = (
            gmail_service.users().messages().send(userId="me", body=create_message).execute()
        )

        if logger is not None:
            logger.info("Sent email with subject '{}' to {}".format(subject, recipients + cc + bcc))

    except HttpError as error:

        if logger is not None:
            logger.error("An error occurred when sending email: {error}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_arguments = parser.add_argument_group("required arguments")
    required_arguments.add_argument("--sender", help="email address of the sender", required=True)
    required_arguments.add_argument(
        "--credentials", help="Gmail API credentials file", required=True
    )
    required_arguments.add_argument("--token", help="Gmail API token file", required=True)
    required_arguments.add_argument(
        "--recipients", help="list of email addresses of the recipents", required=True, nargs="+"
    )
    required_arguments.add_argument("--subject", help="email subject", required=True)
    required_arguments.add_argument("--contents", help="email contents", required=True)
    parser.add_argument(
        "--cc", help="list of email addresses in carbon copy", nargs="+", default=[]
    )
    parser.add_argument(
        "--bcc",
        help="list of email addresses in blind carbon copy",
        nargs="+",
        default=[],
    )
    parser.add_argument("--attachments", help="list of files to attach", nargs="+", default=[])
    args = parser.parse_args()

    credentials = authenticate_google_oauth2(Path(args.credentials), Path(args.token))

    send_mail(
        args.subject,
        args.contents,
        credentials,
        args.sender,
        args.recipients,
        args.cc,
        args.bcc,
        [Path(a) for a in args.attachments],
    )
