
def read_keys():
    keyDict = {}
    with open("resources/APIKey.txt", "r") as file:
        for line in file:
            (key, val) = line.split()
            keyDict[key] = val

    print(keyDict)
    return keyDict