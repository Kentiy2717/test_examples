def mergeTwoLists(list1, list2):
    list_3 = []
    print(len(list1))
    for i in range(len(list1)):
        if list1[i] == list2[i] or list1[i] >= list2[i]:
            list_3.extend([list1[i], list2[i]])
        else:
            list_3.extend([list2[i], list1[i]])
    return list_3

print(mergeTwoLists([1,2,4], [1,3,4]))
print()
print()
print()