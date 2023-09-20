import os 
filepath = input("Enter filepath")
if os.path.isdir(filepath):
    os.chdir(filepath)
    fileNames = os.listdir(filepath) 

    if len(fileNames) == 0: 
        print("Folder empty \n")
    else: 
        print("Folder not empty \n")
        print(fileNames)
else:
    print("File doesn't exist \n")


""" To do list
Need a click and drag file box UI to change the file path to the dragged
file.
C:/Users/firei/OneDrive/Documents/A Software/A music folder
"""