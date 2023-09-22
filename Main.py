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