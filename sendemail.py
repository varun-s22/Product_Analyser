from dotenv import load_dotenv
import os
import smtplib

load_dotenv()

# gets the information from .env file
EMAILID = os.getenv("EMAILID")
PASSWORD = os.getenv("PASSWORD")
SERVER = os.getenv("server")


def send_email(reciever_email, extracted, url):
    # sends email to the user, when called
    product = extracted.title
    price = extracted.price
    connection = smtplib.SMTP(SERVER)
    connection.starttls()
    connection.login(user=EMAILID, password=PASSWORD)
    connection.sendmail(from_addr=EMAILID, to_addrs=reciever_email,
                        msg=f"Subject:PRODUCT {product} available at a cheaper price!!\n\nHey there,\nThe product you have been keeping an eye on {product} is now available at a price of Rs{price}\nGo ahead and grab it at {url}")
    connection.close()
