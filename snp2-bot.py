import gc
import glob
import os
import random
import signal
import sys
import time
from Tkinter import Image

def signal_handler(signum, frame):
	print "Now exiting..."
	exit()

signal.signal(signal.SIGINT, signal_handler)

# Environment setup
os.chdir(os.path.dirname(__file__))
sys.path.append("C:\automa\library.zip")
from automa.api import *

Config.wait_interval_secs = 0.1

# Figure out which window to use
switch_to('Edgebee')

# Global definitions go here
employees = glob.glob("employees/*.png")

# Array of things that should always be clicked
always_click = [
	"buttons/start.png",
	"buttons/closebtn.png", 
	"buttons/closecomponentmissing.png", 
	"buttons/closeitemselect.png", 
	"buttons/closeitembroken.png",
	"buttons/ok.png",
	"buttons/small-ok.png",  # needed for achievements
	"buttons/small-ok-2.png",  # needed for can't select items
	"buttons/next.png", 
	#"customer-interactions/refuse.png",
	#"customer-interactions/sorry.png",
	#"customer-interactions/ok.png", # needed for adventures
	"customers/buy.png",
	"customer-interactions/buy.png"
]
# Array of customers and their interactions
customers = glob.glob("customers/*.png")
suggest = "customer-interactions/suggest.png"
customer_interactions = [
	"customer-interactions/buy.png",
	#"customer-interactions/sell.png",
	#"customer-interactions/thanks.png",
	#suggest,
	#"customer-interactions/refuse.png",
	#"customer-interactions/sorry.png"
]

# Array of buttons that need a pause after clicking
sleep_for = [
	"buttons/start.png",
	"buttons/next.png",
	"buttons/done.png"
]

# Initializations for employee build cycles
cycle_path = "build-cycles/"
build_cycle_indexes = {x: -1 for x in os.listdir(cycle_path) if os.path.isdir(os.path.join(cycle_path, x))}
build_cycle_items = {}
for k in build_cycle_indexes.keys():
	print "k is " + str(k)
	print "build_cycle_items[k] is " + os.path.join(cycle_path, k, "*.png")
	build_cycle_items[k] = glob.glob(os.path.join(cycle_path, k, "*.png"))


# Returns whether the given image was clicked 
def clickImage(img, similarity = 0.75): #can not go higher than 0.8 due to close item select button
	print "clickImage " + str(img)
	# Determine if we're going to sleep after click
	sleepy = 0
	if img in sleep_for:
		sleepy = 1
		
	is_suggestion = img == suggest
	
	# Convert to an image
	found = True
	if img == str(img):
		if img == "buttons/next.png":
			similarity = 0.5
		img = Image(img, similarity)
		found = img.exists()
		
	# Search for the image
	print "check for image " + str(img)
	if found:
		print "found image " + str(img)
		try:

			# Click it
			print "click"
			click(img)
			print "before click"
			# Handle customer suggestions
			#if is_suggestion:
			#	suggestSomething()
			
			#if sleepy:
			#	print "sleep " + str(sleepy)
				#time.sleep(sleepy)
		except Exception as e:
			print e
			print "couldn't click it"
			found = False
	return found

# Checks whether an item was built
def wasSuccessful():
	print "wasSuccessful"
	#return not (clickImage("buttons/ok.png") or clickImage("buttons/closecomponentmissing.png"))
	return not clickImage("buttons/closecomponentmissing.png")

# Attempts to interact with an employee
def employeeInteraction(loop=True):
	
	# Check for employees
	found = False
	random.shuffle(employees)
	for img in employees:
		print("check " + str(img))
		if clickImage(img):
			
			if not Image("employee-interactions/empty-queue.png", 0.75).exists():
				# This employee is already building something
				print "empty-queue is not exist"
				clickImage("buttons/closeitemselect.png")
				continue
			
			# Attempt to use a build cycle for that employee+
			print "employeeBuildCycle(img)"
			employee = os.path.basename(img).split(".")[0]
			employeeBuildCycle(employee)
			#if employeeBuildCycle(employee):
			#	found = True
			#	if not loop:
			#		return found
			#	continue # Move on to the next employee
				
			# Otherwise attempt to build a random item
			#targets = find_all(Image("lvl-target.png"))
			#random.shuffle(targets)
			#while len(targets):
			#	target = targets.pop()
			#	if target.y > 600: 
			#		continue # Don't count level targets that are too low
			#	print "attempting to build " + str(target)
			#	if clickImage(target):
			#		if wasSuccessful():
			#			found = True
			#			if not loop:
			#				return found
			#			break
				
			# Time to give up
			clickImage("buttons/closeitemselect.png")
			clickImage("buttons/closeresource.png")
			
	return found

# Attempts to execute the build cycle for the given employee
def employeeBuildCycle(employee):

	itemIndex=0
	while itemIndex < len(build_cycle_items[employee]): 
		itemIndex+=1
		item=build_cycle_items[employee][itemIndex]
		clickImage(item)
		if wasSuccessful():
			break
	#if build_cycle_items[employee] and len(build_cycle_items[employee]): 
	#	build_cycle_indexes[employee] = (build_cycle_indexes[employee] + 1) % len(build_cycle_items[employee])
	#	item = build_cycle_items[employee][build_cycle_indexes[employee]]
	#	print "item is " + str(item)
	#	if clickImage(item):
	#		return wasSuccessful()
		
	#return False

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
			if random.randint(1, 100) <= 5: #5% chance
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
			continue # Don't count level targets that are too low
		print "attempting to suggest " + str(target)
		if clickImage(target):
			if not clickImage("buttons/small-ok.png"):
				return True

def openStore():
	if Image("buttons/start.png").exists():
		clickImage(Image("buttons/start.png"))
	return
		
# Main script execution
print "Now starting..."

while True:
	
	print "check open sytore"
	openStore()
	
	# Keep clicking on employees when available
	print("employeeInteraction")
	employeeInteraction(loop=True)
	
	# Keep clicking on customers when available
	loop = 0
	#while (not Image("summary.png").exists()) and customerInteraction():
	while (not Image("summary.png").exists()):
		print "loop " + str(loop)
		loop = loop + 1
		employeeInteraction(loop=False) # Check for an employee again
		if loop > 8:
			break
	
	# Check for other buttons and such only if nothing else matched
	for img in always_click:
		clickImage(img)
	
	while clickImage("buttons/done.png"):
		pass
	
	print "Garbage collected " + str(gc.collect()) + " objects"