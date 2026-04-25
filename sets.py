#Contains only unique items
#Can add or delete from a set
#Can NOT modify a set
#You can add elements with .add()
#You can add multiple elems with .update() which is a list
#Use .clear() to clear a set
#Use del to delete a set
#Only contains unique elements you can turn a list into a set
#and remove any duplicates
#Not Indexable
#Unordered
#O(1) check time to see if something exists in a set
#{}


st = set()

st = {'item1', 'item2', 'item3', 'item4'}

fruits = {'mango', 'orange', 'banana', 'apple'}
print(len(fruits))

#add an item
fruits.add('peach')
fruits.add("lime")

#add a list
fruits.update(['lemon', 'watermelon', 'strawberry'])
print(fruits)

#Remove an item
fruits.remove("banana")
print(fruits)

removed_item = fruits.pop()
print(removed_item)

#list to set
num_lst = [1,1,1,1,2,2,3,3,3,3,4,4,4,5,5,5,5,6,6,6,7,7]
num_set = set(num_lst)
print(num_set)

#combining two sets
st1 = {1,2,3,4}
st2 = {1,2,5,6,7,8}
set3 = st1.union(st2)
print(set3)

print(st1.intersection(st2))

#Exercises:
companies = {'Facebook', 'Google', 'Microsoft', 'Apple', 'IBM', 'Oracle', 'Amazon'}
A = {19, 22, 24, 20, 25, 26}
B = {19, 22, 20, 25, 26, 24, 28, 27}
age = [22, 19, 24, 25, 26, 24, 25, 24]

print(len(companies))
companies.add('Twitter')
companies.update(['SpaceX', 'OpenAI', 'Claude'])
print(companies)

companies.remove('Google')

st3 = A.union(B)
print(A.intersection(B))
print(A.issubset(B))
print(A.isdisjoint(B))

ages = set(age)

