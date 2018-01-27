import smtplib
__author__ = 'xaled'


def send_html(email_subject, body_of_email, recipient, gmail_username, gmail_password):
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