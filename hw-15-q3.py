'''
    Author:
    Day 15 Homework - Problem #3

    Using the formula from question 2. Answer the following question:
    Which city has the higher "feels like" temperature: Blacksburg or
    New York?

    Print the name of the city as response, or "Same" if appropriate.
'''

import weather

weatherNY = weather.get_report("New York")
weatherBB = weather.get_report("Blacksburg")
print(weatherNY)
print(weatherBB)
temperatureNY = 44
windNY = 5
windchillNY= temperatureNY - windNY ** 0.7
temperatureBB = 28
windBB = 7
windchillBB = temperatureBB - windBB ** 0.7
print(windchillNY)
print(windchillBB)