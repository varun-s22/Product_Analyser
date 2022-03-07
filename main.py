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
from flask import Flask, render_template, request
from textblob import TextBlob
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigCanvas
import sqlite3

# declaring the namedtuple
data = namedtuple("data", ["source", "title",
                  "price", "photo", "reviews", "rating"])

# header to be passed in soup
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}

# logos of the vendor
AMAZON_LOGO = f"http://media.corporate-ir.net/media_files/IROL/17/176060/Oct18/Amazon%20logo.PNG"
FLIPKART_LOGO = f"https://logos-world.net/wp-content/uploads/2020/11/Flipkart-Logo.png"


def is_amazon(link):
    # checks if the link is of amazon
    amazon = re.search(r'https?://www.amazon.in', link)
    if(amazon is None):
        return False
    return True


def is_flipkart(link):
    # checks if the link is of flipkart
    flipkart = re.search(r'https?://www.flipkart.com', link)
    if(flipkart is None):
        return False
    return True


def isATable(c, tname):
    # checks if the table exists in database
    c.execute(
        f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tname}'")
    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        return True
    return False


def extract_flipkart_info(soup):
    # extracts info
    product_price = soup.find(id="container").text.split("₹")
    for ele in product_price:
        # matches the price-like pattern
        match = re.match(r"^(\d{1,},)?(\d{1,},)?\d{3}$", ele)
        if(match):
            # returns the price
            product_price = match.group()
            break

    product_title = soup.find("h1").text.strip()
    product_photo = soup.find(attrs={"alt": product_title})["src"]

    reviews = soup.find(id="container").text.split("Report Abuse")
    extracted_reviews = []
    for i in range(1, len(reviews)):
        rating = reviews[i][0]
        if(rating != "5" and rating != "4" and rating != "3" and rating != "2" and rating != "1"):
            # checks if the obtained info is a review or QNA
            break
        temp = reviews[i].split("READ MORE")
        rew = temp[0]
        if(not rew):
            continue
        # performs sentiment analysis on the reviews extracted

        sentiment_analysis = TextBlob(rew[1:]).sentiment
        extracted_reviews.append((rating, rew[1:], sentiment_analysis))

    ratings = soup.find(id="container").text.split("★")[0]
    product_rating = ratings[-3:]

    # stores all the extracted info into the namedtuple
    extracted = data("Flipkart", product_title,
                     product_price.strip(), product_photo, extracted_reviews, product_rating)
    return extracted


def price_graph(graph_data):
    # gets the corresponding image of the graph
    fig = graph_data[0]
    # converts graph to image
    output = io.BytesIO()
    FigCanvas(fig).print_png(output)
    # sends data into streams of bytes
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(output.getvalue()).decode('utf8')
    return pngImageB64String


def extract_amazon_info(soup):
    # extracts info
    extracted = soup.find(attrs={"data-a-color": "price"}).text
    product_price = extracted.split(".")[0]
    if(product_price[0] == "₹"):
        product_price = product_price[1:]

    # extracts the data
    product_title = soup.find(id="productTitle").text.strip()
    product_photo = soup.find(attrs={"alt": product_title})["src"]
    product_rating = soup.find(attrs={"data-hook": "rating-out-of-text"}).text

    reviews = soup.find_all(attrs={"data-hook": "review"})
    extracted_reviews = []
    for rew in reviews:
        text_from_review = rew.text
        first_ele = text_from_review.split("\n")[0]
        # gets rating by the reviewer
        match = re.search(r"\d.\d", first_ele)
        rating = "-"
        if(match):
            rating = match.group()

        # gets the review
        review = text_from_review.split("\n\n")
        extracted_review = review[1]

        # perform sentiment analysis on the review extracted
        sentiment_analysis = TextBlob(extracted_review).sentiment
        extracted_reviews.append(
            (rating, extracted_review, sentiment_analysis))

    extracted_data = data("Amazon", product_title, product_price.strip(
    ), product_photo, extracted_reviews, product_rating)
    return extracted_data


app = Flask(__name__)

# flask server


@app.route("/", methods=["POST", "GET"])
def home():
    if(request.method == "POST"):
        # on submitting info to the page
        # extracts the info, from the page
        url = request.form["url"]
        user_email_id = request.form["email"]
        user_price = request.form["desiredPrice"]

        if(not is_amazon(url) and not is_flipkart(url)):
            # if invalid url
            return render_template("finaldata.html", error_msg="Sorry, we couldn't process your request")

        # makes a GET request to the page
        req = requests.get(url=url, headers=header)
        if(req.status_code == 200):
            # if request was successfull
            soup = BeautifulSoup(req.text, "lxml")
            if(is_amazon(url)):
                extracted_data = extract_amazon_info(soup)
            elif(is_flipkart(url)):
                extracted_data = extract_flipkart_info(soup)
        else:
            # if any error encountered
            return render_template("finaldata.html", error_msg="Sorry, we couldn't process your request")

        # gets price vs date graph
        graph_data = get_graph(extracted_data)
        # takes out the maximum and minimum price of the product reached
        minimum_price = graph_data[1]
        maximum_price = graph_data[2]
        # gets the image format of the graph
        pngImageB64String = price_graph(graph_data)

        # connects with the database
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        if(isATable(cur, "userinfo")):
            cur.execute(f"SELECT * FROM userinfo WHERE url ='{url}'")
            # gets all the users interested for a particular link
            if(cur.fetchall()):
                # checks the database, if there are interested users
                for tup in cur.fetchall():
                    # fetches all the user
                    if(convert_price_to_int(extracted_data.price) <= convert_price_to_int(tup[2])):
                        # if the product's current price reached their favoured price or below that
                        # it sends an email to the user
                        send_email(tup[0], extracted_data, url)

        else:
            # if table doesn't exist
            # creates a table
            cur.execute(
                f"CREATE TABLE userinfo(email text,url text,price text)")
        if(user_price and user_email_id):
            # if the user enters his email and favoured amount, then he/she shall get registered on the database
            cur.execute(
                f"INSERT INTO userinfo VALUES('{user_email_id}','{url}','{user_price}')")

        # closes the connection with database
        conn.commit()
        conn.close()

        # writes data into the csv file
        with open("data.csv", "a") as csvfile:
            writer2 = writer(csvfile)
            writer2.writerow([datetime.date.today().strftime(
                "%d/%m/%Y"), extracted_data.source, extracted_data.title, extracted_data.price])

        # gives the logo of the vendor
        if(extracted_data.source == "Amazon"):
            logo = AMAZON_LOGO
        else:
            logo = FLIPKART_LOGO
        return render_template("finaldata.html", source=extracted_data.source, title=extracted_data.title, price=extracted_data.price, photo=extracted_data.photo, rating=extracted_data.rating, reviews=extracted_data.reviews, image=pngImageB64String, logo=logo, maximum_price=maximum_price, minimum_price=minimum_price)

    # returns the home page if GET method
    return render_template("index.html")


if(__name__ == "__main__"):
    # runs the server
    app.run()
