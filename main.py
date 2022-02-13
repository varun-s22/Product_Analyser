from bs4 import BeautifulSoup
import requests
from collections import namedtuple
from csv import reader, writer
import re

data = namedtuple("data", ["title", "price"])


def extract_flipkart_info(soup):
    container = soup.find(
        id="container").contents[0].contents[2].contents[0].contents[1].contents[1].contents[-1].contents
    extracted = data(
        container[0].text.strip(), container[-1].contents[0].contents[0].text.split("₹")[1].strip())
    return extracted


def extract_amazon_info(soup):
    extracted = soup.find(attrs={"data-a-color": "price"}).text
    product_price = extracted.split(".")[0]
    if(product_price[0] == "₹"):
        product_price = product_price[1:]
    product_title = soup.find(id="productTitle").text
    extracted_data = data(product_title.strip(), product_price.strip())
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
url = input("Enter url: ")
if(not is_amazon(url) and not is_flipkart(url)):
    print("Not a valid url")
    exit()
req = requests.get(url=url, headers=header)
if(req.status_code == 200):
    soup = BeautifulSoup(req.text, "html.parser")
    if(is_amazon(url)):
        extracted_data = extract_amazon_info(soup)
    elif(is_flipkart(url)):
        extracted_data = extract_flipkart_info(soup)
    print(extracted_data.title, extracted_data.price)
else:
    print("Server issues!!, Data can't be retrieved. Sorry!!")
