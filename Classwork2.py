# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 19:22:55 2016

@author: Romeo
"""


import crime
import matplotlib.pyplot as plt


rate = crime.get_property_crimes("virginia")
rate2 = crime.get_property_crimes("texas")
print(rate)
print(rate2)
plt.plot(rate)
plt.plot(rate2)
plt.show()
