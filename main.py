# this library allows us to perform data processing
# we can parse websites, csv, etc.
# it can help us transform foreign data types into things we can use in python
import pandas as pd
# this library will help us validate dates
from datetime import datetime
# this library will help us print tabular data
from tabulate import tabulate
# this library allows us to plot graphs, make charts, etc.
import matplotlib.pyplot as plt

# define the file path to the CSV file
FILE_PATH = "Daily_Transit_Ridership.csv"
# the date format used in the dataset
DATE_FORMAT = "%m/%d/%Y"

# read the file path into a pandas DataFrame
frame = pd.read_csv(FILE_PATH)

"""
turn our dataframe into something we can loop over and filter
the itertuples() function turns each row into a python "tuple"
a tuple is similar to a list
in our case, each row would look something like
Pandas(Index=210, Agency='San Francisco BART Rail', Mode='Transit', Date='09/03/2022', _4=36, _5=90241, Year=2022)
we can access data inside of tuples, like `tuple[0]` <- this would grab the first value, since indexes start at 0
"""
rows = list(frame.itertuples())

ridership_data = {
    "San Francisco BART Rail": [],
    "New York City MTA Rail": [],
    "WMATA Bus and Rail": [],
}

# we can use this function to determine whether
# any given row is a part of a specific transit agency
# as well as perform additional validations


def validate_data(data: tuple, agency: str) -> bool:
    data_agency = data[1]
    data_date = data[3]
    data_week_number = data[4]
    data_ridership = data[5]
    data_year = data[6]

    # check if we are in the correct agency
    if data_agency != agency:
        return False

    # try parsing the date into a python date object
    # if it fails (throws an error) we know it is invalid
    # and as such, we will return False
    try:
        datetime.strptime(data_date, DATE_FORMAT)
    except ValueError as e:
        print(e)
        print(f'invalid date: {data_date}')
        return False

    # check if week number, ridership, or year is something other than a number
    if not isinstance(data_week_number, int) or not isinstance(data_ridership, int) or not isinstance(data_year, int):
        print('data is not numeric')
        print(data_week_number, data_ridership, data_year)
        return False

    # check if week number, ridership, and year values are over 0
    if int(data_week_number) < 0 or int(data_ridership) < 0 or int(data_year) < 0:
        print('data is under 0')
        print(data_week_number, data_ridership, data_year)
        return False

    return True


"""
here we use that function we just defined to filter the data to
just rows that are part of the San Francisco BART Rail agency 
we are using the filter() function in python
the filter object takes a function, and some kind of list or iterable
in this case, we are giving it all of the rows in our dataset
then, it checks each row with the function from above to see if it is part
of the SF agency
"""
ridership_data["San Francisco BART Rail"] = list(filter(
    lambda data: validate_data(
        data, "San Francisco BART Rail"),
    rows
))

ridership_data["WMATA Bus and Rail"] = list(filter(
    lambda data: validate_data(
        data, "WMATA Bus and Rail"),
    rows
))

ridership_data["New York City MTA Rail"] = list(filter(
    lambda data: validate_data(
        data, "New York City MTA Rail"),
    rows
))

# now that we have processed the CSV, we can now begin our main data processing
# we will loop over every transit agency agency
# and then collect the data
for agency in ridership_data:
    # in our loop, we are given the name of the agency
    # we need to access the actual data for that given agency
    # by indexing our ridership_data table
    rows = ridership_data[agency]

    monthly_ridership = {}
    weekly_ridership = {}

    for row in rows:
        date_str = row[3]
        date = datetime.strptime(date_str, DATE_FORMAT)

        # if the month we are looking for
        # is not already present in the monthly_ridership map
        # then we will create an empty list for it
        if monthly_ridership.get(date.month) is None:
            monthly_ridership[date.month] = []

        # do the same thing for weekday
        if weekly_ridership.get(date.weekday()) is None:
            weekly_ridership[date.weekday()] = []

        # add row to the correct month/weekday
        monthly_ridership[date.month].append(row)
        weekly_ridership[date.weekday()].append(row)

    monthly_averages = {}
    weekly_averages = {}

    for month in range(0, 12):
        monthly_averages[month] = 0

    # for every month, we will grab the month and its respective datapoints
    for month, datapoints in monthly_ridership.items():
        # just get the list of ridership numbers
        # we don't care about anything else
        ridership = [datapoint[5] for datapoint in datapoints]

        # sum up the ridership numbers, and divide by the amount of data points
        # if the number of data points is 0, we will just automatically make the average
        # 0 since we can't divide by 0
        monthly_averages[month] = sum(
            ridership) / len(ridership) if ridership else 0

    # same thing for weeks
    for week, datapoints in weekly_ridership.items():
        ridership = [datapoint[5] for datapoint in datapoints]

        weekly_averages[week] = sum(ridership) / \
            len(ridership) if ridership else 0

    print(f"Averages for {agency}")

    tabular_monthly_averages = [
        (month, f"{avg:.2f}") for month, avg in monthly_averages.items()]
    tabular_weekly_averages = [(month, f"{avg:.2f}")
                               for month, avg in weekly_averages.items()]

    print(tabulate(tabular_monthly_averages, headers=[
          "Month #", "Average Ridership"], tablefmt="grid"))
    print(tabulate(tabular_weekly_averages, headers=[
          "Weekday #", "Average Ridership"], tablefmt="grid"))

    # create weekly and monthly data for the plot
    monthly_x = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "Novermber", "December"]
    monthly_y = list(monthly_averages.values())

    weekly_x = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    weekly_y = list(weekly_averages.values())

    # create the monthly chart
    monthly_fig = plt.figure(figsize=(15, 5))

    plt.bar(monthly_x, monthly_y, color='blue')

    plt.xlabel("Month")
    plt.ylabel("Average Monthly Ridership")
    plt.title("Average Ridership Accross 12 Months")
    plt.savefig("monthly_ridership.png")

    # create the weekly chart
    weekly_fig = plt.figure(figsize=(10, 5))

    plt.bar(weekly_x, weekly_y, color='blue')

    plt.xlabel("Weekday")
    plt.ylabel("Average Ridership")
    plt.title("Average Ridership Per Weekday")
    plt.savefig("weekly_ridership.png")
