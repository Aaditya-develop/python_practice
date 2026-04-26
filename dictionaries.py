empty_dict = {}

dct = {'key1':'value1', 'key2': 'value2', 'key3': 'value3', 'key4': 'value4'}
person = {
    'first_name':'Asabeneh',
    'last_name':'Yetayeh',
    'age':250,
    'country':'Finland',
    'is_marred':True,
    'skills':['JavaScript', 'React', 'Node', 'MongoDB', 'Python'],
    'address':{
        'street':'Space street',
        'zipcode':'02210'
    }
    }
print(len(dct))

print(dct['key1'])
print(dct.get('key2'))

#Adding to a dictionary
dct['key5'] = 'value5'
person['skills'].append('Java')
print(person)

#Modifying in the dictionary
dct['key1'] = 'value-one'

#Check iof key is in dict
print(dct['key6']) #False

#Removing keys
person.pop('key2') #Removes specifies item
person.popitem() #removes last item

print(persons.values())