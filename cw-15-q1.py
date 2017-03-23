'''
    Author:
    Day 15 Classwork - Problem #1

    The algorithm in this exercise tries to answer this question:
        What is the price per page of a given book?
    The information necessary to make this calculation is inside
    a dictionary.
   
   The dictionary has three keys:
        "number_of_pages"
        "price"
        "discount"
    Put the pieces of this algorithm in the right order to calculate
    the answer.
'''
book = {"number_of_pages":285, "price":99.23, "discount":0.1}
book["price"] 
book["number_of_pages"]
discount = book["price"] * book["discount"]
price_after_discount = book["price"] - discount
price_per_page =  price_after_discount / book["number_of_pages"]
print(price_per_page)





