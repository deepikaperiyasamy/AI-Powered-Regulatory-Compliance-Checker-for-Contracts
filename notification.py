import smtplib
from email.mime.text import MIMEText
import requests
import os

# first we will add the email part 

def send_notification(subject, notification):
    
    # Send notification using SMTP Protocol

    # try:
    #     sender = "infosysintern502@gmail.com"
    #     password = "imkj jnsy cfob duhe"
    #     receiver = "trailmail502@gmail.com"

    #     # create message
    #     msg = MIMEText(f"{notification}")
    #     msg["Subject"]=subject
    #     msg["From"]= f"Deepika <{sender}>"
    #     msg["To"]= receiver

    #     #connect to the Gmail SMTP server
    #     with smtplib.SMTP("smtp.gmail.com", 587) as server:
    #         server.starttls() #start TLS encrytion
    #         server.login(sender, password)
    #         server.send_message(msg)
            
    #     print("✅ Email sent successfully!!!!")
        
    # except Exception as e:
    #     print("Error Occured",e)

    # Send notification using slack



    try:

        WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

        message = {
            "username": "NotificationBot 💬",
            "icon_emoji": ":Sheild:",  # change emoji as you like
            "text": f"*{subject}*\n{notification}"
        }
        print(subject)

        response = requests.post(WEBHOOK_URL, json=message)

        if response.status_code == 200:
            print("✅ Slack notification sent successfully!!!!")
        else:
            print(f"⚠️ Failed to send notification. Status: {response.status_code}")

    except Exception as e:

        print("Error Occurred:", e)
