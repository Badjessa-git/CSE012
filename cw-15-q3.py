'''
    Author:
    Day 15 Classwork - Problem #3

    Write a program that answers the following question:
    Given the current temperature and humidity,
        what it the current weather like?
    Consider the following logic:
        - If the temperature is below 32 degrees and the humidity is
        at least 50%, it is "snowing".
        - If the temperature is above 32 degrees and the humidity is
        at least 50%, it is "raining".
        - Otherwise, it is "clear".
    Fill in the blanks for the dictionary in the code and test your
    code within the various ranges described above.
    For the final submission use the following weather: 29, 55 and 13
    for temperature, humidity and wind respectively.
'''

# This is a comment, they are used to write notes inside the code
# Information written after a # is disregarded by the computer when
# running the program
# The first 18 lines in this file are a multi-line comment

# Change the values in this dictionary to test your program
# Submit the code with the values in the problem description

current_weather = { "temperature":29, "humidity":55, "wind":13}
if current_weather["temperature"] < 32 and current_weather["humidity"] >= current_weather["humidity"] / 2:
    print("snowing")
elif current_weather["temperature"] > 32 and current_weather["humidity"] >= current_weather["humidity"] / 2:
    print("raining") 
else:
    print("clear")
# You will need an if-elif-else block to apply your tests.
# Remember to print the state of the weather exactly as described.
