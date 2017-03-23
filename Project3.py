# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 17:54:39 2016

@author: Romeo
What is/are the most common site(s) of cancer between the brain, the female breast and the corpus?
Is there a correlation between the average age and the count?
Is cancer more common in female or male or both?
Which has a higher concentration of site between delaware, New Jersey, North Carolina?
"""

import cancer
import matplotlib.pyplot as plt
"""
area = cancer.by_area()
site = cancer.by_site()
age = cancer.by_age()

# You can also get all of the sites/areas/ages by not passing in anything
all_sites_cancer = cancer.by_site()
"""
count = 0 
count1 = 0
count2 = 0 
count4 = 0
count5 = 0
count6 = 0
count8 = 0
count3 = 0
count7 = 0
site_list = cancer.by_site()
age_list = cancer.by_age()
area_delaware = cancer.by_area("Delaware")
area_newjersey = cancer.by_area("New Jersey")
area_northcaro = cancer.by_area("North Carolina")
all_sites_cancer = cancer.by_site()
for site in site_list:
    if site["site"] == "Brain":
        count = count + 1
    elif site["site"] == "Female Breast":
        count1 = count1 + 1
    elif site["site"] == "Corpus":
        count2 = count2 + 1
print(count, count1, count2)
if count > count1 and count > count2:
    print("The most common site is the Brain")
if count1 > count and count1 > count2:
    print("The most common site is the Female Breast")
if count2 > count and count2 > count1:
    print("The most common site the Corpus")
if count == count1:
    print("The most common sites are both the Brain and the Female Breast")
if count1 == count2:
    print("The most common sites are both the Female breast and the Corpus")
if count2 == count:
    print("The most common sites are both the Brain and the Corpus")

### The most commons site of cancer is the female breast and the corpus

for site in site_list:
    if site['sex'] == 'Female':
        count3 = count3 + 1
    elif site['sex'] == 'Male':
        count4 = count4 + 1
    elif site["sex"] == "Male and Female":
        count5 = count5 + 1
print(count3, count4, count5)
if count3 > count4 and count3 > count5:
    print("The Cancer sites are most common in Females")
if count4 > count3 and count4 > count5:
    print("The Cancer sites are most common in Males")
if count5 > count3 and count5 > count4:
    print("The Cancer sites are most common in both Males and Females")
###The cancer site that are most common are both in Male and Female

for delaware in area_delaware:
    count6 = count6 + 1
for newjer in area_newjersey:
    count7 = count7 + 1
for northcar in area_northcaro:
    count8 = count8 + 1
print(count6, count7, count8)
if count6 > count7 and count6 > count8:
    print("The highest Concentration area is Delaware")
elif count7 > count6  and count7 > count8:
    print("The highest concentration area is New Jersey")
elif count8 > count6 and count8 > count7:
    print("The highest concentration area is North Carolina")
elif count6 == count7 and count6 == count8:
    print("The concentration is equal in each of the areas")
    
agee=[]
listf=[]
for age in all_sites_cancer:
    agee.append(age['age_adjusted_rate'])     
    listf.append(age['count'])
del agee[0]
del listf[0]

plt.scatter(agee, listf, c='b', marker='+')
# Label Axis
plt.xlabel('Counts')
plt.ylabel('Average Age')
plt.title('Comparison of Counts by Average Age')

# Display bar chart
plt.show()
plt.clf()
print('There seems to be a correlation between lower ages and the count of cancer incident suggesting that cancer mortality is greater at a younger age')


