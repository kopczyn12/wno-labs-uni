import os
import ssl
import smtplib
from email.message import EmailMessage
import smtplib, ssl
import os
import email
import imaplib


def send_email_mech(email_receiver, email, subject):    
    port = 465  
    smtp_server = "smtp.gmail.com"
    sender = "test123141231@gmail.com"
    password = os.environ.get("EMAIL_PASSWORD")
    mail = EmailMessage()
    mail['Subject'] = subject
    mail['From'] = sender
    mail['To'] = email_receiver
    msg = email
    mail.set_content(msg)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, email_receiver, mail.as_string())
    print("Mail has been sent!")
    
def receive_mail_mech():
    server='imap.gmail.com'
    mail=imaplib.IMAP4_SSL(server)
    sender = "test123141231@gmail.com"
    password = os.environ.get("EMAIL_PASSWORD")
    mail.login(sender, password)
    mail.select('inbox')
    status,data=mail.search(None,'All')
    mail_ids=[]
    sender_data = []
    subject_data = []
    content_data = []
    counter = 0
    for block in data:
        mail_ids+=block.split()

    for i in mail_ids:
        
        status, data=mail.fetch(i,'(RFC822)')

        for response_part in data:
            if isinstance(response_part,tuple):
                message=email.message_from_bytes(response_part[1])
                mail_from=message['from']
                mail_subject=message['subject']
                if message.is_multipart():
                    mail_content=''
                    for part in message.get_payload():
                        if part.get_content_type()=='text/plain':
                            mail_content += part.get_payload(decode=True).decode('utf-8')
                else:
                    mail_content = message.get_payload(decode=True).decode('utf-8')
                sender_data.append(mail_from)
                subject_data.append(mail_subject)
                content_data.append(mail_content)
                counter+=1
    return sender_data, subject_data, content_data, counter
