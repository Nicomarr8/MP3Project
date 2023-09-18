import os 
import random
#The names function displays the names of the files.
#To be able to change file path we need UI click and drag file path


filepath = "C:/Users/firei/OneDrive/Documents/A Software/A music folder"
fileNames = os.listdir(filepath)#use methods in OS to locate where this folder is

# The shuffle function include the button to click
print(fileNames)
random.shuffle(fileNames)
print (fileNames)
