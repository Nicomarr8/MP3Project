import os 
import random


filepath = "C:/Users/firei/OneDrive/Documents/A Software/A music folder"
if os.path.isdir(filepath):
    fileNames = os.listdir(filepath) 
    if len(fileNames) == 0: 
        print("Folder empty \n")
    else: 
        print("Folder not empty \n")
        print(fileNames)
        #The shuffle function 
        random.shuffle(fileNames)
        print (fileNames)
else:
    print("File doesn't exist")


""" To do list
Need a click and drag file box UI to change the file path to the dragged
file.
Need button that says shuffle
checked one condition

"""