import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your Gmail email address and password
email = "tedx_sac@staloysius.edu.in"
password = "vzxv ozgu dvwo hxad"

# Recipient's email address
to_email = "ruvelm+tedxtest@outlook.com"

# Create the message
subject = "Test email 1"
body = "Excepteur consectetur voluptate amet fugiat pariatur nulla laborum proident dolor ex sint non."

msg = MIMEMultipart()
msg["From"] = email
msg["To"] = to_email
msg["Subject"] = subject

# Attach the body to the message
msg.attach(MIMEText(body, "plain"))

# Connect to the Gmail SMTP server and send the email
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)

    text = msg.as_string()
    server.sendmail(email, to_email, text)
    server.quit()
    print("Email sent successfully.")
except Exception as e:
    print("Error sending email:", e)
