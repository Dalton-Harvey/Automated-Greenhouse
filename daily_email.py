import LocalTime
import umail
import socket
from time import sleep

def Get_Credentials():
    with open('secrets/email_credentials') as credentials:
        sender = credentials.readline()
        password = credentials.readline()

    return (sender,password)

def Get_Recipients():
    recipients = []
    with open('secrets/recipient_emails') as file:
        for email in file:
            recipients.append(email.strip())

    return recipients

def send_email(subject, body):
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
    sender, password = Get_Credentials()    
    recipients = Get_Recipients()
    try:
        smtp.login(sender, password)
        smtp.to(recipients)
        smtp.write(f'From:{sender}\n')
        smtp.write(f'Subject:{subject}\n')
        smtp.write(body)
        smtp.send()
    except Exception as e:
        print('Failed to send email:', e)
    finally:
        smtp.quit()
        print('Successfully sent email')



def Daily_Email(moist_avgs):
    CurrTime = LocalTime.GetTime()

    if CurrTime[0] == 19 and CurrTime[1] == 30:
        subject = "Daily Moisture Levels"
        body = f"Moisture Average for the day with a per hour breakdown:\n{moist_avgs}"
        send_email(subject, body)
        sleep(60)#Make sure an email isn't sent twice during the same minute
