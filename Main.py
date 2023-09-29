from msilib.schema import ListBox
from textwrap import fill
from tkinter import *
from tkinter import ttk
from turtle import down
from PIL import ImageTk, Image
import json
import eyed3
from pygame import mixer
import os 
def configure_frames():
    window.grid_rowconfigure(0, weight=1)  # Allow the top row (containing left and right frames) to expand vertically
    window.grid_columnconfigure(0, weight=1)  # Allow the first column (containing left frame) to expand horizontally
    window.grid_columnconfigure(1, weight=1)  # Allow the second column (containing right frame) to expand horizontally
    window.grid_rowconfigure(1, weight=1)  # Allow the bottom row (containing down frame) to expand vertically

def GetFilePath():
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

# default settings dictionary
DEFAULT_SETTINGS = {
    "visual_theme": "default",
    "liked_songs": [],
    "account_info": {
        "username": None
    },
    "audio_settings": {
        "volume": 50,
        "equalizer": {
            "bass": 0,
            "treble": 0
        }
    },
    "preferences": {
        "language": "English",
        "notifications": True
    },
    "about_info": {
        "version": 0,
        "developer": False,
        "website": False,
        # "Information about the app"
           }
}

# load settings from the JSON file
def load_settings():
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
    except FileNotFoundError:
        settings = DEFAULT_SETTINGS
    return settings

# Save settings to the JSON file
def save_settings(settings):
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

#Load settings at the beginning of your program
current_settings = load_settings()

# Access and update settings as needed
visual_theme = current_settings["visual_theme"]
liked_songs = current_settings["liked_songs"]
username = current_settings["account_info"]["username"]
volume = current_settings["audio_settings"]["volume"]
bass = current_settings["audio_settings"]["equalizer"]["bass"]
treble = current_settings["audio_settings"]["equalizer"]["treble"]
language = current_settings["preferences"]["language"]
notifications = current_settings["preferences"]["notifications"]
app_version = current_settings["about_info"]["version"]
developer = current_settings["about_info"]["developer"]
website = current_settings["about_info"]["website"]

# Function to change settings
def change_settings(new_settings):
    for key, value in new_settings.items():
        if key in current_settings:
            current_settings[key] = value
        else:
            print(f"Invalid setting: {key}")

def testChangeSettings():
  # Changing settings
  new_settings = {
      "visual_theme": "dark",
      "audio_settings": {
          "volume": 75,
          "equalizer": {
              "bass": 2,
              "treble": -1
          }
      },
      "preferences": {
          "language": "French",
          "notifications": False
      }
  }

  # Apply the new settings
  change_settings(new_settings)

  # Save the updated settings
  save_settings(current_settings)

# directory = "C:/Users/mteag/Music/4K YouTube to MP3/Carry On.mp3"

def tagInfo(directory):
  mp3 = eyed3.load(directory)

  trackTitle = mp3.tag.title
  trackArtist = mp3.tag.artist
  trackAlbum = mp3.tag.album
  trackRD = mp3.tag.getBestDate() 

  if trackTitle == None: trackTitle = "Unknown"
  if trackArtist == None: trackArtist = "Unknown"
  if trackAlbum == None: trackAlbum = "Unknown"
  if trackRD == None: trackRD = "Unknown"

  print("Title: ", trackTitle)
  print("Artist: ", trackArtist)
  print("Album: ", trackAlbum)
  print("Release: ", trackRD)

co1 = 'white'
co2 = "#3C1DC6"
co3 = "#333333"
co4= "#CFC7F8"

window = Tk()
window.title("")
window.geometry('325x225')
window.configure(background = co1)
window.resizable(width = TRUE, height = TRUE)
window.state('zoomed')



#frames
left_frame = Frame(window, width = 150, height = 150, bg = co1)
left_frame.grid(row=0, column=0, padx=1, pady=1,sticky="nsew")
right_frame = Frame(window, width = 250, height = 150, bg = co3)
right_frame.grid(row=0, column=1, padx=0, sticky="nsew")
down_frame = Frame(window, width = 400, height = 100, bg = co4)
down_frame.grid(row=1, column=0,columnspan=3, padx=0, pady=1, sticky="nsew")


# Creating a scrollbar
my_scrollbar = Scrollbar(right_frame, orient=VERTICAL)

# Creating a listbox
listbox = Listbox(right_frame, yscrollcommand=my_scrollbar.set)
listbox.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

# Configure scrollbar
my_scrollbar.config(command=listbox.yview)
my_scrollbar.grid(row=0, column=1, sticky="ns")

# Configure grid for right_frame (parent container)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

#images
img_1=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/mp3.png")
img_1 = img_1.resize((130,130))
img_1=ImageTk.PhotoImage(img_1)
app_image = Label(left_frame, height =130, image=img_1, padx=10, bg=co1)
app_image.place(x=10,y=15)

#play button
img_2=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/play.png")
img_2 = img_2.resize((30,30))
img_2=ImageTk.PhotoImage(img_2)
play_button = Button(down_frame, height =40,width = 40, image=img_2, padx=10, bg=co1)
play_button.grid(row=0,column=2, sticky="S")


#prev button
img_3=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/previous.png")
img_3 = img_3.resize((30,30))
img_3=ImageTk.PhotoImage(img_3)
prev_button = Button(down_frame, height=40, width=40, image=img_3, padx=10, bg=co1)
prev_button.grid(row=0,column=1, sticky="s")

#next button
img_4=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/next.png")
img_4 = img_4.resize((30,30))
img_4=ImageTk.PhotoImage(img_4)
next_button = Button(down_frame, height =40,width = 40, image=img_4, padx=10, bg=co1)
next_button.grid(row=0,column=3, sticky="s")


#pause button
img_5=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/pause.png")
img_5 = img_5.resize((30,30))
img_5=ImageTk.PhotoImage(img_5)
pause_button = Button(down_frame, height =40,width = 40, image=img_5, padx=10, bg=co1)
pause_button.grid(row=0,column=4, sticky="s")


#continue button
img_6=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/continue.png")
img_6 = img_6.resize((30,30))
img_6=ImageTk.PhotoImage(img_6)
continue_button = Button(down_frame, height =40,width = 40, image=img_6, padx=10, bg=co1)
continue_button.grid(row=0,column=5, sticky="s")


#stop button
img_7=Image.open("C:/Users/kibet/OneDrive/Desktop/Fall 2023/CS-250/Class Project/MP3 Project UI - Images (1)/stop.png")
img_7 = img_7.resize((30,30))
img_7=ImageTk.PhotoImage(img_7)
stop_button = Button(down_frame, height =40,width = 40, image=img_7, padx=10, bg=co1)
stop_button.grid(row=0,column=6, sticky="s")

# seek bar
seek= Scale(down_frame, from_=0, to =100, orient=HORIZONTAL)
seek.grid (row=0, column=7)


configure_frames()  # Call the configure_frames function to make the frames resizable
window.mainloop()
# #mixer.music.pause() - this is how to pause the music
# #mixer.music.unpause() - this is how to unpause the music
