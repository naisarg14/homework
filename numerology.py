from string import ascii_lowercase
from itertools import permutations

def calculate_name(name):
    letter_values = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
        'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
        's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8
    }

    name = name.lower().replace(" ", "")
    sum = 0
    for i in name:
        if i.isdigit():
            sum += int(i)
        try:
            sum += letter_values[i]
        except:
            pass
    print(sum)
    return sum

def add_digits(n):
    sum = 0
    for i in str(n):
        sum += int(i)
    if sum <= 9:
        return sum
    else:
        print(sum)
        return add_digits(sum)

while True:
    print(add_digits(calculate_name(input("Enter your Name: "))))

#for permutation in permutations(ascii_lowercase, 6):
 #   if add_digits(calculate_name("Bhawna patel " + " ".join(permutation))) == 1:
        #print("Bhawna patel " + " ".join(permutation))