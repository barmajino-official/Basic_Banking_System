
import time
import json
import random
import string
import pandas as pd
import operator
from datetime import datetime

from prettytable import PrettyTable





Setting = json.load(open("./src/Setting.json"))


def getRandomString(StartWith = ""):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return StartWith.join(random.choice(letters+"0123456789") for i in range(4))

def openFileRequired(files):
    return {key.strip() : open(data).read() for (key,data) in files.items()}
     #[open(file).read() for file in files]

def convertFileDatatocsv(data, files):
    for (key,path) in files.items():
        
        df = pd.DataFrame([i for i in data[key].values() ])
        df.to_csv(path, index=False, header=False)

def convertFileDataToDict(data, Setting):
    resultDict = dict()
    for (key, config) in Setting.items():
        DataDict = dict()
        listOfLinesData = data[key].split("\n")
        lineContentDataListFormList = [linesData.split(",") for linesData in listOfLinesData]
        for lineData in lineContentDataListFormList:
            tempDataDict = {key.strip() : data.strip() for (key,data) in zip(config["key"], lineData)}
            if len(tempDataDict[config["SetIndexAsPrimaryKey"]]): DataDict[tempDataDict[config["SetIndexAsPrimaryKey"]]] = tempDataDict
        resultDict[key]= DataDict
    return resultDict


def GetInput(data, type_, operation, key, setting, ISunique = False):
    if operation == "random": return getRandomString()
    if operation == "auto" and type_ == "TIMESTAMP" :
        return str(time.time())

    InputRuningPermition = True
    message = f"Enter {key} :\t"
    isLIST = False
    if(type_ == "LIST"):
        isLIST = True
        type_ = "int"
        print("Select one of this index :")
        for i in range(len(setting[key])):
            print(f"* {i} - {setting[key][i]}")
    while(InputRuningPermition):
        try:
            input_ = eval(type_)(input(message))
            if(type_ == "str"): input_ = input_.strip()
            else: pass
            if isLIST : input_ = setting[key][input_]
            else: pass
            if(operation == "unique"):
                InputRuningPermition = [i.get(key, False) == input_  for i in data.values() ].count(True)
                message = f"this username ({input_}) alredy taken :\t"
            else: InputRuningPermition = False

            if(ISunique):
                InputRuningPermition = True
                resultlist = [i.get(key, False) == input_  for i in data.values() ]
                t = resultlist.count(False)
                message = f"this {key} ({input_}) not exist try again :\t"
                if(len(resultlist)-t == 1):
                    InputRuningPermition = False
                else: pass
            else: pass
        except:
            if(operation == "unique"):
                message = f"this {key} ({input_}) alredy taken :\t"
            if(operation == "required"):
                message = f"enter valide {key} :\t"
                if isLIST : message = f"enter valide number of {key} :\t"
    return input_
GetInput.title = "dynamic input"

# Admin menue functions

def displayStatistics(UsersDataDict):
    result = [i.get("GENDER", False).lower() for i in UsersDataDict["users"].values()]
    my_table = PrettyTable()

    my_table.field_names = Setting["GENDER"]

    my_table.add_row([result.count(key.lower()) for key in Setting["GENDER"]])

    print(my_table)
    input("Press \"Enter\" to continue...")
displayStatistics.title = "Display Statistics"

def addAnEmployee(UsersDataDict):
    newuser = dict()
    for key in Setting["FileConfig"]["users"]["key"]:
        data = Setting["addData"]["users"][key]
        newuser[key] = str(GetInput(UsersDataDict["users"], data[1],data[0],key, Setting  ))
    UsersDataDict["users"][newuser["ID"]] = newuser
    return UsersDataDict
addAnEmployee.title = "Add an Employee"

def DisplayEmployees(UsersDataDict):
    data = [ i for i in UsersDataDict["users"].values()]
    data.sort(key=operator.itemgetter('TIMESTAMP'))
    datacopy = data.copy()

    my_table = PrettyTable()

    my_table.field_names = Setting["FileConfig"]["users"]["key"]
    for i in datacopy:
        list_ = []
        for key,value in i.items():
            if(key == 'TIMESTAMP'):
                list_.append(datetime.fromtimestamp(float(value)).strftime('%d-%m-%Y %H:%M:%S'))
            else: list_.append(value)
        my_table.add_row(list_)
    print(my_table)
    input("Press \"Enter\" to continue...")
DisplayEmployees.title = "Display all Employees"

def updateSalary(UsersDataDict):
    id = GetInput(UsersDataDict["users"], "str", "unique", "ID", None, ISunique = True)
    salary = GetInput(UsersDataDict["users"], "float", "required", "SALARY", None)
    
    UsersDataDict["users"][id]["SALARY"] = salary

    return UsersDataDict
updateSalary.title = "Change Employee's Salary"

def removeAnEmployee(UsersDataDict):
    id = GetInput(UsersDataDict["users"], "str", "unique", "ID", None, ISunique = True)
    UsersDataDict["users"].pop(id)
    return UsersDataDict
removeAnEmployee.title = "Remove Employee"

def raiseSalary(UsersDataDict):
    id = GetInput(UsersDataDict["users"], "str", "unique", "ID", None, ISunique = True)
    raise_ = GetInput(UsersDataDict["users"], "float", "required", "Raise Percentage", None)
    UsersDataDict["users"][id]["SALARY"] = str(float(UsersDataDict["users"][id]["SALARY"]) + ((float(UsersDataDict["users"][id]["SALARY"]) * raise_) / 100))
    return UsersDataDict
raiseSalary.title = "Raise Employee's Salary"

# user menue functions

def setUserLog(UsersDataDict, status):
    data = dict()
    if(UsersDataDict["usertype"] != Setting["admin"]["username"]):
        for i in Setting["FileConfig"]["userslog"]["key"]:
            if(i == "MESSAGE"):
                data["MESSAGE"] = status
            elif(i == "TIMESTAMP"):
                data["TIMESTAMP"] = time.time()
            elif(i == "LOGID"):
                data["LOGID"] = getRandomString("log_")
            else:
                data[i] = UsersDataDict["users"][UsersDataDict["usertype"]][i]
        UsersDataDict["userslog"][data["LOGID"]] = data


def displayEmployeesLog(UsersDataDict):
    data = [ i for i in UsersDataDict["userslog"].values()]

    my_table = PrettyTable()

    my_table.field_names = Setting["FileConfig"]["userslog"]["key"]
    for i in data:
        list_ = []
        for key,value in i.items():
            if(key == 'TIMESTAMP'):
                list_.append(datetime.fromtimestamp(float(value)).strftime('%d-%m-%Y %H:%M:%S'))
            else: list_.append(value)
        my_table.add_row(list_)
    print(my_table)
    input("Press \"Enter\" to continue...")
displayEmployeesLog.title = "Display Employees log"


def getUserSalary(UsersDataDict):
    my_table = PrettyTable()
    my_table.field_names = ["Salary"]
    my_table.add_row([UsersDataDict["users"][UsersDataDict["usertype"]]["SALARY"]])
    print(my_table)
    input("Press \"Enter\" to continue...")

getUserSalary.title = "Check my Salary"

# login menue function
def login(filesDataDict):
    isruning = True
    while(isruning):
        logindata = (GetInput(None, "str", "required", "USERNAME", None),GetInput(None, "str", "required", "Password", None))
        if(len(logindata[1])):
            if(logindata == (Setting["admin"]["username"], Setting["admin"]["password"]) ):
                filesDataDict["usertype"] = Setting["admin"]["username"]
                isruning = False
            else: print("incorect username and/or password")
        else:
            if([i.get("USERNAME", False) == logindata[0]  for i in filesDataDict["users"].values() ].count(True)):
                for i in filesDataDict["users"].values():
                    if i.get("USERNAME", False) == logindata[0]:
                        filesDataDict["usertype"] = i.get("ID", False)
                        setUserLog(filesDataDict, "Login")
                        isruning = False
            else:
                print(f"we cant find username -> {logindata[0]}")
login.title = "Login"

def ExitSystem(filesDataDict):
    setUserLog(filesDataDict, "Logout")
    convertFileDatatocsv(filesDataDict,Setting["FileRequired"])
    login(filesDataDict)
ExitSystem.title = "Exit"

def DisplayMenue(filesDataDict):
    functions = [displayStatistics,addAnEmployee,DisplayEmployees, displayEmployeesLog ,updateSalary,removeAnEmployee,raiseSalary,getUserSalary, ExitSystem]

    if(filesDataDict["usertype"] == "admin"):
        selectedFunc = GetInput(None, "LIST","required","index of Admin Menue", Setting  )
        
    else:
        selectedFunc = GetInput(None, "LIST","required","index of User Menue", Setting  )
    for i in functions:
        if(i.title == selectedFunc):
            return i(filesDataDict)

DisplayMenue.title = "display_menue"

def main():
    
    files = openFileRequired(Setting["FileRequired"])
    filesDataDict = convertFileDataToDict(files, Setting["FileConfig"])
    login(filesDataDict)
    while True:
        returnData = DisplayMenue(filesDataDict)
        if(returnData):
            filesDataDict = returnData
    

main()
