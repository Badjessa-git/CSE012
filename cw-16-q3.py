'''
    Author: 
    Day 16 Classwork - Problem #3

    The weather.get_all_forecasted_temperatures returns a list of
    forecasted temperatures for each city in the database. Use the
    data to answer the following question:
        What is the average temperature for each city?

    Fill in the blanks to answer the question.
'''

import weather

all_forecasted_temperatures = weather.get_all_forecasted_temperatures()

for i in all_forecasted_temperatures:
    city_forecast = i["forecasts"]
    city_name = i["city"]
    total = 0
    n = 0
    for temp in city_forecast:
        total = total + temp
        n = n + 1
    average = total/n
    print(city_name, ":", average)
