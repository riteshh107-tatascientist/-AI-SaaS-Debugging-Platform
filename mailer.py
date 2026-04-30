import smtplib
from email.mime.text import MIMEText

ADMIN_EMAIL = "youradmin@gmail.com"

def send_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = ADMIN_EMAIL
        msg["To"] = ADMIN_EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # ⚠️ use app password (not normal password)
        server.login(ADMIN_EMAIL, "YOUR_APP_PASSWORD")

        server.sendmail(ADMIN_EMAIL, ADMIN_EMAIL, msg.as_string())
        server.quit()

        return True
    except:
        return False