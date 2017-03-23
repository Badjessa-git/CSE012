'''
    Author
    Day 16 Classwork - Problem #2

    Use the weather.get_forecasted_reports block to answer this question:
    What is the average forecasted "feels like" temperature in Blacksburg?

    To calculate the "feels like" temperature you need to use this formula:
        feels_like = temperature - wind**0.7
    You can reuse your code from question 2 on the previous day's homework.
'''

import weather

forecast_list = weather.get_forecasted_reports("Blacksburg")
feels_like = 0
feels_like_total = 0
total = 0
for i in forecast_list:
    total = total + 1 
    feels_like = i["temperature"] - i["wind"]**0.7
    feels_like_total = feels_like_total + feels_like
average_feels_like_temperature = feels_like_total / total
# print can take multiple parameters. Separate them with commas.
print("Feels like Temperature: ", average_feels_like_temperature)
