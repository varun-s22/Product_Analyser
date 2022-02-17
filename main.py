from bs4 import BeautifulSoup
import requests
from graph import *
from collections import namedtuple
from csv import writer
import re
import datetime
from sendemail import *
import lxml
import re

data = namedtuple("data", ["source", "title", "price"])


def extract_flipkart_info(soup):
    product_price = soup.find(id="container").text.split("₹")
    for ele in product_price:
        match = re.search(r"^\d{2},\d{3}", ele)
        if(match):
            product_price = match.group()
            break
    product_title = soup.find("h1").text.strip()
    extracted = data("Flipkart", product_title, product_price.strip())
    return extracted


def extract_amazon_info(soup):
    extracted = soup.find(attrs={"data-a-color": "price"}).text
    product_price = extracted.split(".")[0]
    if(product_price[0] == "₹"):
        product_price = product_price[1:]
    product_title = soup.find(id="productTitle").text.strip()
    extracted_data = data("Amazon", product_title, product_price.strip())
    return extracted_data


def is_amazon(link):
    amazon = re.search(r'https?://www.amazon.in', link)
    if(amazon is None):
        return False
    return True


def is_flipkart(link):
    flipkart = re.search(r'https?://www.flipkart.com', link)
    if(flipkart is None):
        return False
    return True


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}
# url = input("Enter url: ")
# if(not is_amazon(url) and not is_flipkart(url)):
#     print("Not a valid url")
#     exit()
url1 = "https://www.amazon.in/New-Apple-iPhone-12-128GB/dp/B08L5TNJHG/ref=sr_1_4?crid=3RU9QCTA3J5F3&keywords=iphone+12&qid=1644838387&sprefix=9rt%2Caps%2C341&sr=8-4"
url2 = "https://www.flipkart.com/apple-iphone-12-blue-128-gb/p/itm02853ae92e90a?pid=MOBFWBYZKPTZF9VG&lid=LSTMOBFWBYZKPTZF9VGIFSM7T&marketplace=FLIPKART&q=iphone+12&store=tyy%2F4io&srno=s_1_2&otracker=search&otracker1=search&fm=Search&iid=583f4a52-3709-4320-b314-5270cd46ae0e.MOBFWBYZKPTZF9VG.SEARCH&ppt=sp&ppn=sp&ssid=l4bz7508s00000001644838374356&qH=7b7504afcaf2e1ea"


if(__name__ == "__main__"):
    # user_price = input("Enter price: ")
    # user_email = input("Enter your email: ")
    req1 = requests.get(url=url1, headers=header)
    req2 = requests.get(url=url2, headers=header)
    with open("data.csv", "a") as csvfile:
        writer = writer(csvfile)
        if(req1.status_code == 200):
            soup1 = BeautifulSoup(req1.text, "lxml")
            if(is_amazon(url1)):
                extracted_data = extract_amazon_info(soup1)

                writer.writerow([datetime.date.today().strftime("%d/%m/%Y"), extracted_data.source,
                                 extracted_data.title, extracted_data.price])
        # if(extracted_data.price <= user_price):
        #     send_email(user_email, extracted_data, url1)

        else:
            print("Server issues!!, Data can't be retrieved. Sorry!!")

        if(req2.status_code == 200):
            soup2 = BeautifulSoup(req2.text, "html.parser")
            if(is_flipkart(url2)):
                extracted_data = extract_flipkart_info(soup2)

                writer.writerow([datetime.date.today().strftime("%d/%m/%Y"), extracted_data.source,
                                extracted_data.title, extracted_data.price])
                # if(extracted_data.price <= user_price):
                # send_email(user_email, extracted_data, url2)
                # get_graph(extracted_data)
        else:
            print("Server issues!!, Data can't be retrieved. Sorry!!")
