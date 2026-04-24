#print(), len(), type(), int(), float(), str(), 
#input(), list(), dict(), min(), max(), sum(), 
#sorted(), open(), file(), help(), and dir()

name = "Aaditya"
age = 20
print(len("Hello World!")) #Len counts all spaces and letters in a string
print("Name", name, "Age", age)

question = input('What makes you happy?')
print(question)

#Data Types
# Different python data types
# Let's declare variables with various data types

first_name = 'Asabeneh'     # str
last_name = 'Yetayeh'       # str
country = 'Finland'         # str
city= 'Helsinki'            # str
age = 250                   # int, it is not my real age, don't worry about it

# Printing out types
print(type('Asabeneh'))          # str
print(type(first_name))          # str
print(type(10))                  # int
print(type(3.14))                # float
print(type(1 + 1j))              # complex
print(type(True))                # bool
print(type([1, 2, 3, 4]))        # list
print(type({'name':'Asabeneh'})) # dict
print(type((1,2)))               # tuple
print(type(zip([1,2],[3,4])))    # zip

#Casting:

age = 20
age_float = float(age)
print(age_float)

name = "Ronaldo"
name_list = list(name)
print("namelist", name_list)


#Exercises
first_name = "Aaditya"
last_name = "Chandola"
full_name = "Aaditya Chandola"
country = "United States"
city = "Monmouth Junction"
is_married = False
is_true = False
is_light_on = False
firstVar, secondVar, thirdVar = 1,2,3

print(type(first_name))
print("Length of First name", len(first_name))
print("Length of First name", len(first_name), "Length of Last name", len(last_name))
num_one = 5
num_two = 4
total = num_one + num_two
diff = num_two - num_one
product = num_two * num_one
division = (num_two / num_one)
remainder = num_two % num_one
#exp = num_one.pow(num_two)
floor_division = num_one // num_two

radius = 30
#area_of_circle = 