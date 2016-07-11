myList = [[1] * 4] * 3
#This is equivalent to:
#lst1 = [1]*4
#myList = [lst1]*3
myList[1][1] = 7
print myList

#When you write [x]*3 you get, essentially, the list [x, x, x]. That is, a list with 3 references to x. When you then change x all three references are changed.
#To fix it, you need to make sure that you create a new list at each position. One way to do it is

betterList = [[1]*4 for n in range(3)]
betterList[1][1] = 7
print betterList

