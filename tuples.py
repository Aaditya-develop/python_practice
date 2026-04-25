#Once a tuple is created, we can not change its values
#You can only delete the entire tuple, not a singular item
#You can change tuple to list if you want to edit it
#Fixed Data that doesnt change
#Everything else is the same 

empty_tuple = tuple()

tpl = ('item1', 'item2', 'item3')

fruits = ('banana', 'orange', 'apple', 'lemon')

print(len(tpl))
first_item = tpl[0]
second_item = tpl[1]
last_item = len(tpl) - 1
last_tpl_item = tpl[last_item]

first_three_fruits = fruits[0:3]
neg_first_fruits = fruits[-4:-1]

lst = list(fruits)
lst.insert(0, 'pear')
print(lst)

for i in range(len(fruits)):
    if fruits[i] == 'orange':
        print("FOund")
        
tpl_fruits = tpl + fruits
print(tpl_fruits)

#Exercises
empty_tpl = ()
brothers = ('vikram', 'karan', 'aarav')
sisters = ('diya',) #You need a comma to make it a tuple

siblings = brothers + sisters
print(siblings, len(siblings))

lst = list(siblings)
lst.append('vivek')
lst.append('deepika')
family_members = lst.copy()
