"""
Email sending python module.
"""

# standard packages
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def total_size(files_list):
    """
    Get total size of given list of files.
    Input:
        -files_list     [str, ...]
    """
    size = 0
    for file in files_list:
        size += os.path.getsize(file)
    return size


def send_mail(
    sender,
    password,
    recipient,
    cc,
    bcc,
    subject,
    contents,
    attachments,
    smtp_server,
    smtp_port,
):
    """
    Send email.
    Input:
        -sender         str
        -password       str
        -recipient      str
        -cc             [str, ...]
        -bcc            [str, ...]
        -subject        str
        -contents       str
        -attachments    [str, ...]
            list of files to attach
        -smtp_server    str
        -smtp_port      int
    """

    # creating message object
    message = MIMEMultipart()

    # adding sender, recipient, CC, BCC, and subject
    message["From"] = sender
    message["To"] = recipient
    message["CC"] = ",".join(cc)
    message["BCC"] = ",".join(bcc)
    message["Subject"] = subject

    # handle attachment
    attachment_size = total_size(attachments)
    if attachment_size > 10000000:  # case of oversize attachment
        contents += "\nOversized attachment."
    else:
        for file in attachments:
            attachment_filename = os.path.basename(file)
            piece = open(file, "rb")  # opening report file
            part = MIMEBase(
                "application", "octet-stream"
            )  # encoding attachment in Base64
            part.set_payload((piece).read())  # reading report file in attachment
            encoders.encode_base64(part)  # encoding attachment in Base64
            part.add_header(
                "Content-Disposition", "piece; filename= {}".format(attachment_filename)
            )
            message.attach(part)

    # adding contents of the email
    message.attach(MIMEText(contents.encode("utf-8"), "plain", "utf-8"))

    # connection with server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.set_debuglevel(1)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender, password)

    # converting message object in utf-8 encoded string
    encoded_message = message.as_string().encode("utf-8")

    # sending email
    server.sendmail(sender, [recipient] + cc + bcc, encoded_message)

    # disconnecting with server
    server.quit()
