import base64
from operator import mod
import zlib
import gzip
import json
import PIL.Image
import win32clipboard
import PIL
import cv2
from os import listdir
from os.path import isfile, join
from selenium import webdriver as wd
from selenium.webdriver.common.by import By

dataJson = open("data.json", "r")
txt = dataJson.read()
data = json.loads(txt)
level_name = data["compilingProperties"][0]["levelName"]
debug_mode = data["compilingProperties"][0]["debugMode"]
replaceOldObjects = data["compilingProperties"][0]["replaceOldObjects"]
geode_integration = data["compilingProperties"][0]["geode_integration"]
printDebugInfo = data["compilingProperties"][0]["printDebugInfo"]
pathToData = data["compilingProperties"][0]["pathToData"]
if geode_integration == True:
    debug_mode = True

class Object:
    def __init__(self,objId: int, **kwargs):
        self.index = addObj(objId, **kwargs)
    def addGroups(self, group_list: list):
        global objectsList, __groupList
        if __isObjectHasGroups(objectsList[self.index]) == False:
            objectsList[self.index] += ",57,"
        iterationCount = 0
        for group in group_list:
            iterationCount += 1
            if callable(group):    
                freeGroup = group()
                if objectsList[self.index][len(objectsList[self.index])-1] != ",":  
                    objectsList[self.index] += "." + str(freeGroup)
                else:
                    objectsList[self.index] += str(freeGroup)
            else:
                if objectsList[self.index][len(objectsList[self.index])-1] != ",":  
                    objectsList[self.index] += "." + str(group)
                else:
                    objectsList[self.index] += str(group)
                __groupList.append(group)
    def setColor(self, h: float, s: float, v: float):
        objectsList[self.index] += f",41,1,43,{h}a{s}a{v}a1a0"


def __addToClipBoard(string: str):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(string)
    win32clipboard.CloseClipboard()
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

def debugLog(value): # accepts any value that can be printed with print() func
    if printDebugInfo == True:
        print(f"[DEBUG] {value}")

def __xor(string: str, key: int) -> str:
    return ("").join(chr(ord(char) ^ key) for char in string)

def __decrypt_data(data: str) -> str:
    base64_decoded = base64.urlsafe_b64decode(__xor(data, key=11).encode())
    decompressed = gzip.decompress(base64_decoded)
    return decompressed.decode()

def __encrypt_data(data: str) -> str:
    compressed = gzip.compress(data.encode())
    b64_encoded = base64.urlsafe_b64encode(compressed)
    readyStr = __xor(b64_encoded.decode(), key = 11).encode()
    return readyStr.decode()

def __decode_level(level_data: str, is_official_level: bool) -> str:
    if is_official_level:
        level_data = 'H4sIAAAAAAAAA' + level_data
    base64_decoded = base64.urlsafe_b64decode(level_data.encode())
    # window_bits = 15 | 32 will autodetect gzip or not
    decompressed = zlib.decompress(base64_decoded, 15 | 32)
    return decompressed.decode()

def __encode_level(level_string: str, is_official_level: bool) -> str:
    gzipped = gzip.compress(level_string.encode())
    base64_encoded = base64.urlsafe_b64encode(gzipped)
    if is_official_level:
        base64_encoded = base64_encoded[13:]
    return base64_encoded.decode()

objectsList = [] # list of EVERY object that will be pasted in file after running script
__decodedDatString = None   
__rawDataString = None
__decodedData = ""
__decodedLevel = None
__rawDataFile = None
__objectsString = ""
__oldLevelString = ""
__oldDataString = ""
__groupList = []

def getLevelString():
    global __rawDataString, __rawDataFile
    __rawDataFile = open(pathToData,"r+")
    __rawDataString = __rawDataFile.read()

def start():
    if geode_integration == False:
        global __decodedData, __decodedLevel, __oldDataString, __oldLevelString
        getLevelString()
        __decodedData = __decrypt_data(__rawDataString)
        __oldDataString = __decodedData
        levelNameIndexInData = __decodedData.find("<s>"+level_name+"</s>")
        __decodedLevel = __decodedData[levelNameIndexInData+3:]
        __decodedLevel = __decodedLevel[(__decodedLevel.find("<s>")+3):]
        __decodedLevel = __decodedLevel[:(__decodedLevel.find("</s>"))]
        __oldLevelString = __decodedLevel
        __decodedLevel = __decode_level(__decodedLevel, False)

def addObj(obj_id: int, **kwargs) -> int: # this func is PARENT of all functions that spawn groups, so it's like a "manager". Returns index of object in the object list
    global objectsList, __objectsString
    objectString = f"1,{obj_id}"
    objectKeys = open("objectKeys.txt", "r")
    for objectProperties in objectKeys.readlines():
        name = objectProperties[:objectProperties.find(" ")]
        key = objectProperties[objectProperties.find(" ")+1:objectProperties.rfind(" ")]
        type = objectProperties[objectProperties.rfind(" ")+1:].rstrip("\n")
        property = registerProperties(name,key,type,**kwargs)
        if property != None:
            objectString += property
    # default xPos and yPos properties
    if kwargs.get("xPos") == None:
        objectString += f",2,0"
    if kwargs.get("yPos") == None:
        objectString += f",3,0"
    # things that hard to automatizate
    
    if kwargs.get("borders") != None:
        objectString += f",203,{kwargs["borders"][0]},204,{kwargs["borders"][1]},205,{kwargs["borders"][2]},206,{kwargs["borders"][3]}"
    if kwargs.get("blendingMode") != None:
        if kwargs["blendingMode"] == "Normal":
            pass
        elif kwargs["blendingMode"] == "Additive":
            objectString += f",174,1"
        elif kwargs["blendingMode"] == "Multiply":
            objectString += f",174,{2}"
        elif kwargs["blendingMode"] == "Invert":
            objectString += f",174,{3}"
    if kwargs.get("gradientLayer") != None:
        layers = ["bg","mg","b5","b4","b3","b2","b1","p","t1","t2","t3","t4","g","ui","max"]
        objectString += f",202,{layers.index(kwargs["gradientLayer"])+1}"
    if kwargs.get("easing") != None:
        layers = ["None","EaseInOut","EaseIn","EaseOut","ElasticInOut","ElasticIn","ElasticOut",
                  "BounceInOut","BounceIn","BounceOut","ExponentalInOut","ExponentalIn",
                  "ExponentalOut","SineInOut","SineIn","SineOut","BackInOut","BackIn","BackOut"]
        objectString += f",30,{layers.index(kwargs["easing"])}"
    if kwargs.get("stopTriggerMode") != None:
        if kwargs.get("Pause"):
            __objectsString += f",580,1"
        elif kwargs.get("Resume"):
            __objectsString += f",580,2"
    if kwargs.get("onlyX") != None:
        if kwargs["onlyX"] == True:
            objectString += f",101,1"
    if kwargs.get("onlyY") != None:
        if kwargs["onlyY"] == True:
            objectString += f",101,2"
    if kwargs.get("distance") != None:
        objectString += f",396,{kwargs["distance"]*3}"
    if kwargs.get("conditionType") != None or kwargs.get("modifyValueType"):
        if kwargs["conditionType"] == "Larger" or kwargs["modifyValueType"] == "Multiply":
            objectString += f",88,1"
        if kwargs["conditionType"] == "Smaller" or kwargs["modifyValueType"] == "Divide":
            objectString += f",88,2"
    if kwargs.get("noMultiactivate") != None:
        objectString += f",444,{int(not kwargs["noMultiactivate"])}"

    #################
    objectString += ",155,1"
    objectsList.append(objectString)
    return len(objectsList)-1

def addString(objectString: str):
    global objectsList
    objectsList.append(objectString)


def registerProperties(name,key,type, **kwargs) -> str:
    buffer = ""
    if kwargs.get(name) != None:
        if type == "bool":
            buffer += f",{key},{int(kwargs[name])}"
            return buffer
        elif type == "float" or type == "int":
            buffer += f",{key},{kwargs[name]}"
            return buffer
        elif type == "pointList":
            buffer += f",{key},"
            for group in kwargs[name]:
                if group != kwargs[name][len(kwargs[name])-1]:
                    buffer += str(group) + "."
                else:
                    buffer += str(group)
            return buffer
        elif type == "text":
            buffer += f",{key},{base64.b64encode(kwargs[name].encode()).decode()}"
            return buffer

def __addObjectsWithPointDelimiter(obj_index: int, group_list: list):
    global objectsList
    objectsList[obj_index] += ",57,"
    for group in group_list:
        if group != group_list[len(group_list)-1]:
            objectsList[obj_index] += str(group) + "."
        else:
            objectsList[obj_index] += str(group)
    objectsList[obj_index] += ",155,1"

def toggleTrigger(targetGroupID: int, **kwargs) -> Object:
    return Object(1049, targetGroupID = targetGroupID, **kwargs)

def gravityTrigger(gravity: float, **kwargs) -> Object:
    return Object(2066, gravity = gravity, **kwargs)

def timeWarpTrigger(timeMod: float, **kwargs) -> Object:
    return Object(1935, timeMod = timeMod, **kwargs)

def gradientTrigger(vertexMode, **kwargs) -> Object:
    return Object(2903,vertexMode = vertexMode, **kwargs)

def moveTrigger(targetGroupID: int, duration: float, **kwargs) -> Object:
    return Object(901, targetGroupID = targetGroupID, duration = duration, **kwargs)

def spawnTrigger(targetGroupID: int, **kwargs) -> Object:
    return Object(1268,targetGroupID = targetGroupID, **kwargs)

def scaleTrigger(targetGroupID: int, **kwargs) -> Object:
    return Object(2067,targetGroupID = targetGroupID, **kwargs)

def eventTrigger(targetGroupID: int, **kwargs) -> Object:
    return Object(3604,targetGroupID = targetGroupID, **kwargs)

def countTrigger(targetGroupID: int, itemID: int, targetCount: int, **kwargs) -> Object:
    return Object(1611,targetGroupID = targetGroupID, itemID = itemID, targetCount = targetCount, **kwargs)

def instantCountTrigger(targetGroupID: int, itemID: int, targetCount: int, **kwargs) -> Object:
    return Object(1811,targetGroupID = targetGroupID, itemID = itemID, targetCount = targetCount, **kwargs)

def pickupTrigger(itemID: int, targetCount: int, **kwargs) -> Object:
    return Object(1817,itemID = itemID, targetCount = targetCount, **kwargs)

def addCounterLabel(itemID: int, **kwargs) -> Object:
    return Object(1615, itemID = itemID, **kwargs)

def followTrigger(targetGroupID: int, followGroupID, duration: float, **kwargs) -> Object:
    return Object(1347,targetGroupID = targetGroupID, followGroupID = followGroupID, duration = duration, **kwargs)

def collisionBlock(blockID: int, dynamicBlock: bool, **kwargs) -> Object:
    return Object(1816, blockID = blockID, dynamicBlock = dynamicBlock **kwargs)

def stateCollisionBlock(stateOn: int, stateOff: int, **kwargs) -> Object:
    return Object(3640, stateOn = stateOn, stateOff = stateOff, **kwargs)

def collisionTrigger(blockID: int, blockID2: int, targetGroupID: int, **kwargs) -> Object:
    return Object(1815,blockID = blockID, blockID2 = blockID2, targetGroupID = targetGroupID **kwargs)

def intantCollisionTrigger(blockID: int, blockID2: int, trueID:int, falseID: int, **kwargs) -> Object:
    return Object(3609,blockID = blockID, blockID2 = blockID2, trueID = trueID, falseID = falseID)

def randomTrigger(groupID: int, groupID2: int, chance: int) -> Object:
    return Object(1912,groupID = groupID, groupID2 = groupID2, chance = chance)

def resetTrigger(groupID: int, **kwargs) -> Object:
    return Object(3618, groupID = groupID, **kwargs)

def advRandomTrigger(chances: list, **kwargs) -> Object:
    return Object(2068, chances = chances, **kwargs)

def addText(text : str, **kwargs) -> Object:
    return Object(914, text = text, **kwargs)

def rotateTrigger(targetGroupID: int, centerGroupID: int, **kwargs) -> Object:    # unready
    return Object(1346, targetGroupID = targetGroupID, targetPosGroupID = centerGroupID, **kwargs)

def stopTrigger(targetID, **kwargs) -> Object:
    return Object(1616, targetGroupID = targetID)

def __getKeysOfObject(obj: str) -> list:
    objectKeys = []
    splittedObj = obj.split(",")
    for keyOrProp in range(len(splittedObj)):
        if keyOrProp % 2 == 0: # key
            objectKeys.append(splittedObj[keyOrProp])
    return objectKeys

def __isObjectHasGroups(obj: str) -> bool:
    groups = __getKeysOfObject(obj)
    return groups.count("57")

def nextFreeGroup() -> int:
    global __groupList
    if len(__groupList) == 0:
        __groupList.append(1)
        return 1
    else:
        for i in range(9999):
            if i not in __groupList and i > 0:
                __groupList.append(i)
                return i

def rgbToHSV(r:int,g:int,b:int) -> list:
    r = r/255
    g = g/255
    b = b/255
    Cmax = max(r,g,b)
    Cmin = min(r,g,b)
    delta = Cmax - Cmin
    # H
    h = 0
    if delta == 0:
        h = 0
    elif Cmax == r:
        h = mod((g-b)/delta,6)*60
    elif Cmax == g:
        h = (((b-r)/delta)+2)*60
    elif Cmax == b:
        h = (((r-g)/delta)+4)*60
    # S
    s = 0
    if Cmax == 0:
        s = 0
    if Cmax != 0:
        s = delta/Cmax
    # V
    v = Cmax

    return [h,s,v]

def pixelArtToGD(filePath: str):
    img = PIL.Image.open(filePath)
    width = img.size[0]
    height = img.size[1]
    for w in range(width):
        for h in range(height):
            rgb = img.getpixel([w,h])
            if type(rgb) == int:
                hsv = rgbToHSV(rgb,rgb,rgb)
                Object(955,xPos = w*30, yPos = (h*-30)+500).setColor(hsv[0],hsv[1],hsv[2])
            elif rgb[0] == 0 and rgb[1] == 0 and rgb[2] == 0 and rgb[3] == 0:
                pass
            else:
                hsv = rgbToHSV(rgb[0],rgb[1],rgb[2])
                Object(955,xPos = w*30, yPos = (h*-30)+500).setColor(hsv[0],hsv[1],hsv[2])

def geometrizeToGd(filePath: str, xPos_ = 0, yPos_ = 0):
    dataJson = open(filePath, "r")
    txt = dataJson.read()
    data = json.loads(txt)
    Z = 0
    for object in data:
        Z += 1
        data = object["data"]
        color = object["color"]
        hsvColors = rgbToHSV(color[0],color[1],color[2])
        if object["type"] == 5: # Circles
            Object(1764,
                xPos = data[0] + xPos_,
                yPos = data[1] + yPos_,
                scaling = (data[2]) /4,
                zOrder = Z,
                ).setColor(hsvColors[0],hsvColors[1],hsvColors[2])
        if object["type"] == 4: # rotated Ellipses
            Object(1764, 
                xPos = data[0] + xPos_,
                yPos = data[1] + yPos_,
                scalingX = (data[2]) / 4,
                scalingY = (data[3]) / 4,
                rotation = data[4]*(-1),
                zOrder = Z
                ).setColor(hsvColors[0],hsvColors[1],hsvColors[2])


def __getFilesInFolder(folderPath: str) -> list: 
     return [f for f in listdir(folderPath) if isfile(join(folderPath, f))]

def __getFrame(sec, vidcap, count):
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames,image = vidcap.read()
    if hasFrames:
        cv2.imwrite("image"+str(count)+".jpg", image)     # save frame as JPG file
    return hasFrames

def __cutVideoToFrames(inputFilePath: str, outputFolderPath: str):
    vidcap = cv2.VideoCapture(inputFilePath)
    sec = 0
    frameRate = 0.033 #//it will capture image in each 0.5 second
    count=1
    success = __getFrame(sec, vidcap, count)
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success = __getFrame(sec, vidcap, count)

def videoToJson(pathToVideo: str, outputFolder: str, ):
    print("")
def jsonToGD(pathToJsonFolder: str):
    jsonFilesStr = __getFilesInFolder(pathToJsonFolder)
    for fileStr in jsonFilesStr:
        geometrizeToGd(f"{pathToJsonFolder}\{fileStr}")
def __modifyFile(dataToReplace: str, oldLevelString: str, newObjList: list):
    global __rawDataFile, debug_mode, replaceOldObjects
    newDecodedObjString = ""

    for objStr in newObjList:
        newDecodedObjString += objStr + ";"
    if geode_integration == False:
        __rawDataFile.seek(0)
        decodedOldLevelString = __decode_level(oldLevelString, False)
        decodedOldObjectString = decodedOldLevelString[decodedOldLevelString.find(";")+1:]
        if decodedOldObjectString == "":
            newDecodedLevelString = decodedOldLevelString + newDecodedObjString
        else:
            newDecodedLevelString = decodedOldLevelString.replace(decodedOldObjectString, newDecodedObjString)
        newEncodedLevelString = __encode_level(newDecodedLevelString, False)
        if replaceOldObjects == True:
            newData = dataToReplace.replace(oldLevelString, newEncodedLevelString)
        else:
            oldAndNewLevelString = __decode_level(oldLevelString, False) + newDecodedObjString
            newData = dataToReplace.replace(oldLevelString, __encode_level(oldAndNewLevelString, False))
        if debug_mode == False:
            __rawDataFile.write(__encrypt_data(newData))
        else:
            print(newDecodedObjString)
    else:
        __addToClipBoard(newDecodedObjString)
        print("\n \nSuccesfully added to your clipboard! \nNow you have to paste it using 'Paste' button in Geometry Dash (available with special geode-integration mod) \n \n")
def end():
    global __rawDataFile, objectsList, __oldLevelString, __oldDataString
    
    __modifyFile(__oldDataString, __oldLevelString, objectsList)
    if geode_integration == False:
        __rawDataFile.close()
