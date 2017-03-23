'''
    Author
    Day 16 Classwork - Problem #1

    Use the weather.get_forecasted_reports block to answer this question:
    What is the average wind speed in Blacksburg for the forecasted days?
'''

import weather

forecast_list = weather.get_forecasted_reports("Blacksburg")
total = 0
wind = 0
for i in forecast_list:
    total = total + 1
    wind = wind + i["wind"]
average = wind / total
print(average)
