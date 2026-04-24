age = 20
height = 6.2
complex = 3 + 5j

#1
def triangleArea(base, height):
    base = input("Type the Base ")
    height = input("Type the Height ")
    area = 0.5 * float(base) * float(height)
    print(area)



#2
def sides(sideA, sideB, sideC):
    sideA = input("Enter side a")
    sideB = input("Enter side b")
    sideC = input("Enter side c")
    perm = int(sideA)+int(sideB)+int(sideC)
    print("The perimeter is ", perm)

#3
def rectArea():
    length = input("Get Length ")
    width = input("Get Width ")
    area = float(length) * float(width)
    print("The area is", area)

#rectArea()

#4
def circRadius():
    radius = input("Enjter the Radius ")
    question = input("Do you want to calculate Area or Circumference? (A/C)")
    if question == "A":
        area = 3.14 * float(radius) * float(radius)
        print("Area is ", area)
    elif question == "C":
        circum = 2 * 3.14 * float(radius)
        print("Circumference is ", circum)
        
#circRadius()

#5
print(len("python") != len("dragon"))

print('on' in 'python' and 'on' in 'dragon')

print('jargon' in 'I hope this course is not full of jargon')

stringA = "hellogoodbye"

print(len(stringA))
floatStringA = float(len(stringA))
print(floatStringA)

