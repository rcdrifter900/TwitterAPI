
def __init__(self):
    self.setup()

def get_API_keys():
    keyDict = {}
    with open("resources/APIKey.txt", "r") as file:
        for line in file:
            (key, val) = line.split()
            keyDict[key] = val

    #print(keyDict)
    return keyDict

def get_Payload():
    return ""

def setup():
    ""