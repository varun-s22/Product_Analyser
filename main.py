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


header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}
url = "https://www.amazon.in/New-Apple-iPhone-12-64GB/dp/B08L5VJYV7/ref=sr_1_3?keywords=iphone+12&qid=1644702135&sprefix=iphone%2Caps%2C236&sr=8-3"
url2 = "https://www.amazon.in/Kurkure-Green-Chutney-Rajasthani-Style/dp/B009GIUZNE?pd_rd_w=BCBky&pf_rd_p=ace64564-89b9-4863-a50c-f8acef1159bb&pf_rd_r=SDR83NSMMK2KYH6TAMDY&pd_rd_r=5b5b65b4-f307-43e2-a389-5baeda32daf5&pd_rd_wg=3MQRr&psc=1&ref_=pd_bap_d_rp_18_i"
req = requests.get(url=url2, headers=header)
soup = BeautifulSoup(req.text, "html.parser")
print(soup.find(class_="a-offscreen"))

# extract_tuple = extract_info(soup)
# product_title = extract_tuple.title
# product_price = extract_tuple.price

# with open("data.csv", "w") as csvfile:
#     csv_writer = writer(csvfile)
#     csv_writer.writerow([product_title, product_price])
