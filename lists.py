print("Lists")

#Collection of different Data Types
#It is ordered and modifiable

lst = list()
print(len(lst)) #Empty list

lst = []

fruits = ['apple', 'banana', 'orange', 'lemon']
vege = ['lettuce', 'tomato', 'onion']
countries = ['finland', 'america', 'france']

print("fruits", fruits)
print("fruits", fruits, "length of list", len(fruits))

lst = ['Asabeneh', 250, True, {'country':'Finland', 'city':'Helsinki'}] # list containing different data types

#Negative indexing

first_fruit = fruits[-1]
print(first_fruit)

all_fruits = fruits[0:4]
print(all_fruits)


#if 'banana' in fruits:
 #   print("true")
    
def printFruits():
    print(fruits)
    
def checkTrueFalse() -> bool:
    for i in range(len(fruits)):
        if fruits[i] == 'banana':
            return True
    return False
result = checkTrueFalse()
print(result)

fruits.insert(4, 'mango')
fruits.insert(2, 'peach')
fruits.append('pear')
fruits.remove('peach')
fruit_pop = fruits.pop()
print(fruit_pop)
printFruits()

fruits_copy = fruits.copy()
print(fruits_copy)

fruits_copy.reverse()
print(fruits_copy)

fruits.sort()

print(fruits, "\n\n\n")

#Exercises
def printCompanies():
    print(companies)

print("Exercises")
lst = list()
lst = [1, "hello", 3, 5.5, "bye"]
print(len(lst))
print(lst[0], lst[2], lst[4])
mixed_data_types = ["Aaditya", 20, 6.2, False, "190 Deans Lane"]
print(lst)

companies = ['Facebook', 'Google', 'Microsoft', 'Apple', 'IBM', 'Oracle', 'Amazon']
companies[0] = "OpenAI"
print(companies)
companies.append('Microsoft')
printCompanies()

uppercase=companies[0].upper()
print(uppercase)

if 'Google' in companies:
    print("True")
    


print(companies[3:])

front_end = ['HTML', 'CSS', 'JS', 'React', 'Redux']
back_end = ['Node','Express', 'MongoDB']

front_end.extend(back_end)
print(front_end)
