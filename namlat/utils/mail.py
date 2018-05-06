import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

__author__ = 'xaled'
logger = logging.getLogger(__name__)


def send_html(email_subject, body_of_email, recipient, gmail_username, gmail_password):
    logger.debug("sending mail (%s) to %s", email_subject, recipient)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(gmail_username, gmail_password)
    headers = "\r\n".join(["from: " + gmail_username,
                           "subject: " + email_subject,
                           "to: " + recipient,
                           "mime-version: 1.0",
                           "content-type: text/html"])
    # body_of_email can be plaintext or html!
    content = headers + "\r\n\r\n" + body_of_email
    session.sendmail(gmail_username, recipient, content)


def send_html_ex1(email_subject, body_of_email, recipient, gmail_username, gmail_password):
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(gmail_username, gmail_password)
    msg = MIMEMultipart('alternative')
    msg.set_charset('utf8')
    msg['FROM'] = gmail_username

    msg['Subject'] = Header(email_subject, "utf-8")
    msg['To'] = recipient
    # And this on the body
    _attach = MIMEText(body_of_email.encode('utf-8'), 'html', 'UTF-8')
    msg.attach(_attach)
    session.sendmail(gmail_username, recipient, msg.as_string())
    session.quit()


def send_html_ex2(email_subject, body_of_email, recipient, gmail_username, gmail_password):
    logger.debug("sending mail (%s) to %s", email_subject, recipient)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(gmail_username, gmail_password)
    headers = "\r\n".join(["from: " + gmail_username,
                           "subject: " + email_subject,
                           "to: " + recipient,
                           "mime-version: 1.0",
                           "content-type: text/html; charset=UTF-8"])
    # body_of_email can be plaintext or html!
    content = headers + "\r\n\r\n" + body_of_email
    session.sendmail(gmail_username, recipient, content.encode("utf-8"))
