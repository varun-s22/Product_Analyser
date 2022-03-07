from datetime import datetime
from csv import reader
from collections import defaultdict
from matplotlib.figure import Figure

min_digits = {1: 1, 2: 10, 3: 100, 4: 1000, 5: 10000,
              6: 100000, 7: 1000000, 8: 10000000, 9: 100000000}


def convert_price_to_int(price):
    # converts extracted price to integer, for comparison and plotting
    return int("".join(price.split(",")))


def get_lower_range(num):
    # function to get the lower range of graph to plot
    if(num == 0):
        return 0
    num_of_digits = len(str(num))
    return num-min_digits[num_of_digits]


def get_higher_range(num):
    # function to get the upper range of graph to plot
    if(num == 0):
        return 0
    num_of_digits = len(str(num))
    return num+min_digits[num_of_digits]


def get_data():
    # gets data from the csv file, where all data is stored
    data = defaultdict(lambda: defaultdict(lambda: []))
    with open("data.csv") as csvfile:
        read = reader(csvfile)
        for items in read:
            if(items[0] != "date"):
                data[items[1]][items[2]].append((items[0], items[3]))
    return data


def get_graph(extracted_data):
    # plots the graph, price vs date
    data = get_data()

    # figure, graph shall be sent in form of image
    fig = Figure(figsize=(13, 7), constrained_layout=True)

    product_title = extracted_data.title
    product_platform = extracted_data.source
    x_axis = []
    y_axis = []
    for tup in data[product_platform][product_title]:
        # data being added to list, from csv file
        x_axis.append(datetime.strptime(tup[0], "%d/%m/%Y"))
        y_axis.append(convert_price_to_int(tup[1]))

    if(not y_axis):
        # check, if the product's info is not present in the file
        Minimum_price = 0
        Maximum_price = 0
    else:
        Minimum_price = min(y_axis)
        Maximum_price = max(y_axis)

    lower_range = get_lower_range(Minimum_price)
    upper_range = get_higher_range(Maximum_price)

    # plotting of the graph
    axis = fig.add_subplot(1, 1, 1, ylim=(lower_range, upper_range))
    axis.plot(x_axis, y_axis)
    axis.set_title(product_title, fontweight="bold")
    axis.set_xlabel("Date", fontsize=20, color="brown")
    axis.set_ylabel("Price(in Rs)", fontsize=20, color="brown")
    axis.grid()

    return (fig, Minimum_price, Maximum_price)
