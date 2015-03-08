import gc
import glob
import os
import random
import signal
import sys
import time
from Tkinter import Image
from __builtin__ import str
import datetime
import time

# Define variable
MAXLOOP = 3
MAXRESTTIMES = 4
def signal_handler(signum, frame):
        print "Now exiting..."
        exit()

signal.signal(signal.SIGINT, signal_handler)

# Environment setup
os.chdir(os.path.dirname(__file__))
sys.path.append(r"C:\automa\library.zip")
from automa.api import *

Config.wait_interval_secs = 0.01

# Figure out which window to use
switch_to('Edgebee')

# Global definitions go here
employees = glob.glob("employees/*.png")

# Array of things that should always be clicked
always_click = [        
        "customers/buy.png",
        "customer-interactions/buy.png",
        "buttons/start.png",
        "buttons/closebtn.png",
        "buttons/closecomponentmissing.png",
        "buttons/closeitemselect.png",
        "buttons/closeitembroken.png",
        "buttons/ok.png",
        "buttons/small-ok.png",  # needed for achievements
        "buttons/small-ok-2.png",  # needed for can't select items
        "buttons/next.png",
        "customer-interactions/refuse.png",
        "customer-interactions/sorry.png",
        "customer-interactions/ok.png",
        "buttons/closewhencraging.png",  # needed for adventures
        "buttons/citylevel.png",
        "buttons/klash.png"
]
# Array of customers and their interactions
customers = glob.glob("customers/*.png")
suggest = "customer-interactions/suggest.png"
customer_interactions = [
        "customer-interactions/buy.png",
]

# Array of buttons that need a pause after clicking
sleep_for = [
        "buttons/start.png",
        "buttons/next.png",
        "buttons/done.png"
]

# items that can be sold to customer
suggestionItem = glob.glob("suggestion/*.png")

# Initializations for employee build cycles
cycle_path = "build-cycles/"
build_cycle_indexes = {x:-1 for x in os.listdir(cycle_path) if os.path.isdir(os.path.join(cycle_path, x))}
build_cycle_items = {}
for k in build_cycle_indexes.keys():
        build_cycle_items[k] = glob.glob(os.path.join(cycle_path, k, "*.png"))


# Returns whether the given image was clicked 
def clickImage(img, similarity=0.85):  # can not go higher than 0.8 due to close item select button
        #writeLog("clickImage " + str(img))
        # Determine if we're going to sleep after click
        sleepy = 0
        if img in sleep_for:
            sleepy = 2
                
        # is_suggestion = img == suggest
        
        # Convert to an image
        found = True
        if img == str(img):
            if img == "buttons/next.png":
                    similarity = 0.5
            img = Image(img, similarity)
            found = img.exists()
                
        # Search for the image
        #writeLog("check for image " + str(img))
        if found:
                writeLog("found image " + str(img))
                try:

                        # Click it
                        click(img)
                        # Handle customer suggestions
                        # if is_suggestion:
                        #       suggestSomething()
                        
                        if sleepy:
                                writeLog("sleep " + str(sleepy))
                                time.sleep(sleepy)
                except Exception as e:
                        # writeLog(e)
                        print(e)
                        writeLog("couldn't click it")
                        found = False
        return found

# Checks whether an item was built
def wasSuccessful():
        # return not (clickImage("buttons/ok.png") or clickImage("buttons/closecomponentmissing.png"))
        return not clickImage("buttons/closecomponentmissing.png")

# Attempts to interact with an employee
def employeeInteraction(loop=True):
        
        # Check for employees
        found = False
        random.shuffle(employees)
        for img in employees:
                if clickImage(img):
                        
                    if not Image("employee-interactions/empty-queue.png", 0.75).exists():
                            # This employee is already building something
                            writeLog("queue is not empty")
                            clickImage("buttons/closeitemselect.png")
                            continue
                        
                    # Attempt to use a build cycle for that employee+
                    employee = os.path.basename(img).split(".")[0]
                    employeeBuildCycle(employee)
                        
                    clickImage("buttons/closeitemselect.png")   
                    clickImage("buttons/closeresource.png")
                        
        return found

# Attempts to execute the build cycle for the given employee
def employeeBuildCycle(employee):
        itemIndex = 0
        while itemIndex < len(build_cycle_items[employee]): 
            item = build_cycle_items[employee][itemIndex]
            clickImage(item)
            if wasSuccessful():
                #if renamePng(str(item), '_', '.'):
                #    build_cycle_items[employee].remove(item)
                break
            itemIndex += 1

# Attempts to interact with customers
def customerInteraction():
        found = False
        # Search for customer
        for img in customers:
                if clickImage(img):
                        if not Image("customer-interactions/check-if-opened.png").exists():
                                clickImage("buttons/closeitemselect.png")
                                clickImage("buttons/closeresource.png")
                                clickImage("buttons/closeconstruction.png")
                                continue
                        found = True
                        # Interact with customer
                        for img in customer_interactions:
                                if clickImage(img, 0.95):
                                        break
                        if random.randint(1, 100) <= 5:  # 5% chance
                                # Check for an employee again
                                employeeInteraction(loop=False)
                        
        return found

# Attempts to suggest an item to the customer
def suggestSomething():
        
        # Attempt to build something that we're out of
        targets = find_all(Image("lvl-target.png"))
        random.shuffle(targets)
        while len(targets):
                target = targets.pop()
                if target.y > 600: 
                        continue  # Don't count level targets that are too low
                if clickImage(target):
                        if not clickImage("buttons/small-ok.png"):
                                return True


def sellSuggestionItemsToCustomer(img):
        writeLog("check customer interesting..." + str(img))
        found = False
        if clickImage(img):
                writeLog("found customer")
                found = True
                if Image("customer-interactions/sell.png").exists():
                        writeLog("sell an item to customer " + str(img)) 
                        clickImage(Image("customer-interactions/sell.png"), 0.8)
                else:
                        writeLog("want to sell item to customer but out of item " + str(img)) 
                        suggestionItem.remove(img)
                        os.remove(img)
                        #os.rename(str(img), str(img))
                        clickImage(Image("customer-interactions/refuse.png"), 0.8)
        return found

def openStore():
        if Image("buttons/start.png").exists():
                clickImage(Image("buttons/start.png"))
        return
                
# Main script execution

def writeLog(str):      
        with open("Log.txt", "a") as f:
                t = time.time()
                f.write(datetime.datetime.fromtimestamp(t).strftime('%m-%d %H:%M:%S'))
                f.write(" " + str)
                f.write('\n')
                print str

def renamePng( path, first, last):
    try:
        start = path.index( first ) + len( first )
        end = path.index( last, start )
        num = path[start:end]
        if int(num) == 1:
            writeLog("delete the item from build-cycle" + str(path)) 
            os.remove(path)
            return True
        elif int(num) > 1:
            newNum = int(num) - 1
            newPath = path[0:start] + str(newNum) + path[end:len(path)]
            os.rename(path, newPath)
            writeLog("rename the item to" + newPath)
            return  True
        #nothing will be happened if number is 0
        return False
    except ValueError:
        return ""
            
# print now time
# writeLog(datetime.datetime.now())

restTime = 0
while True:
        writeLog("check open store")
        openStore()
        
        # Keep clicking on employees when available
        # print("employeeInteraction")
        # employeeInteraction(loop=True)
        
        # Keep clicking on customers when available
        loop = 0
        #print (not Image("summary.png").exists())
        #print loop < MAXLOOP
        #print (not Image("summary.png").exists()) & loop < MAXLOOP
        #print False & True
        while (loop < MAXLOOP):
            loop = loop + 1
            employeeInteraction(loop=True)
            for img in suggestionItem:
                    sellSuggestionItemsToCustomer(img)
            if Image("summary.png").exists():
                break;
            if Image("customers/buy.png").exists():
                clickImage("customers/buy.png", 0.8)
                clickImage("customer-interactions/buy.png", 0.8)
            if loop == 2:
                 # Check for other buttons and such only if nothing else matched
                for img in always_click:
                    img = Image(img, 0.8)
                    clickImage(img)
        while clickImage("buttons/done.png"):
            clickImage("buttons/done.png", 0.8)
            pass
        if Image("buttons/next.png").exists():
            clickImage("buttons/next.png", 0.8)
        writeLog("Garbage collected " + str(gc.collect()) + " objects")
