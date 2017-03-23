'''
    Author:
    Day 15 Homework - Problem #2

    Using the wind speed and the temperature, you can approximate the
    "feels like" temperature.
    The formula is roughly: windchill = temperature - wind ** 0.7
    
    Notice that the "**" operator is the "raising to a power" operator.

    Use the formula to answer:
    What is the "feels like" temperature in Blacksburg?
'''
import weather

cw = weather.get_report("Blacksburg")
print(cw)   
temperature = 28
wind = 7
windchill = temperature - wind ** 0.7
print(windchill)

