from main import *
import matplotlib.pyplot as mp
from csv import reader
from collections import defaultdict


def convert_price_to_int(price):
    return int("".join(price.split(",")))


def get_data():
    data = defaultdict(lambda: defaultdict(lambda: []))
    with open("data.csv") as csvfile:
        read = reader(csvfile)
        for items in read:
            if(items[0] != "date"):
                data[items[1]][items[2]].append((items[0], items[3]))
    return data


def get_graph(extracted_data):
    data = get_data()
    product_title = extracted_data.title
    product_platform = extracted_data.source
    x_axis = []
    y_axis = []
    for tup in data[product_platform][product_title]:
        x_axis.append(tup[0])
        y_axis.append(convert_price_to_int(tup[1]))
    mp.plot(x_axis, y_axis, color='navy', marker='o',
            linestyle='dashed', linewidth=2, markersize=12)
    mp.xlabel("Date", fontsize=16, color="brown")
    mp.ylabel("Price(₹)", fontsize=16, color="brown")
    mp.xticks(fontsize=9)
    mp.yticks(fontsize=9)
    mp.title(product_title)
    mp.show()
