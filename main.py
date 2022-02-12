from bs4 import BeautifulSoup
import requests
from collections import namedtuple
from csv import reader, writer


def extract_info(soup):
    data = namedtuple("data", ["title", "price"])
    container = soup.find(
        id="container").contents[0].contents[2].contents[0].contents[1].contents[1].contents[-1].contents
    extracted = data(
        container[0].text, container[-1].contents[0].contents[0].text.split("₹")[1])
    return extracted


req = requests.get("https://www.flipkart.com/apple-iphone-12-black-64-gb/p/itma2559422bf7c7?pid=MOBFWBYZU5FWK2VP&lid=LSTMOBFWBYZU5FWK2VPUYA8BN&marketplace=FLIPKART&q=iphone+12&store=tyy%2F4io&srno=s_1_1&otracker=AS_QueryStore_OrganicAutoSuggest_1_1_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_1_na_na_na&fm=search-autosuggest&iid=8b500cf8-05af-491e-8626-47669c079861.MOBFWBYZU5FWK2VP.SEARCH&ppt=hp&ppn=homepage&ssid=l6jqth7j5c0000001644666303046&qH=7b7504afcaf2e1ea")
if(req.status_code == 200):
    soup = BeautifulSoup(req.text, "html.parser")

    extract_tuple = extract_info(soup)
    product_title = extract_tuple.title
    product_price = extract_tuple.price

    with open("data.csv", "w") as csvfile:
        csv_writer = writer(csvfile)
        csv_writer.writerow([product_title, product_price])
else:
    print("Server issues!!")
