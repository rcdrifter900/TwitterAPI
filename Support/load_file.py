
def read_keys():
    file = open("resources/APIKey.txt", "r")
    keyDict = file.read()
    print(keyDict)
    return keyDict