import tkinter
from PIL import ImageTk, Image
import json
import eyed3
from pygame import mixer
import os 

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

class Window(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry('600x400')
        self.configure(background = "white")
        self.state('zoomed')
        
        #frames
        self.left_frame = tkinter.Frame( width = 150, height = 150, bg = "white")
        self.right_frame = tkinter.Frame( width = 250, height = 150, bg = "#333333")
        self.down_frame = tkinter.Frame( width = 400, height = 100, bg = "#CFC7F8")


        # Creating a scrollbar
        self.my_scrollbar = tkinter.Scrollbar(self.right_frame, orient="vertical")

        # Creating a listbox
        self.listbox = tkinter.Listbox(self.right_frame, yscrollcommand=self.my_scrollbar.set)

        # Configure scrollbar
        self.my_scrollbar.config(command=self.listbox.yview)

        # Configure grid for right_frame (parent container)

        #images
        self.img_1=Image.open("img\\mp3.png")
        self.img_1 = self.img_1.resize((130,130))
        self.img_1= ImageTk.PhotoImage(self.img_1)
        self.app_image = tkinter.Label(self.left_frame, height =130, image=self.img_1, padx=10, bg="white")

        #play button
        self.img_2=Image.open("img\\play.png")
        self.img_2 = self.img_2.resize((30,30))
        self.img_2=ImageTk.PhotoImage(self.img_2)
        self.play_button = tkinter.Button(self.down_frame, height =40,width = 40, image=self.img_2, padx=10, bg="white")


        #prev button
        self.img_3=Image.open("img\\previous.png")
        self.img_3 = self.img_3.resize((30,30))
        self.img_3=ImageTk.PhotoImage(self.img_3)
        self.prev_button = tkinter.Button(self.down_frame, height=40, width=40, image=self.img_3, padx=10, bg="white")

        #next button
        self.img_4=Image.open("img\\next.png")
        self.img_4 = self.img_4.resize((30,30))
        self.img_4=ImageTk.PhotoImage(self.img_4)
        self.next_button = tkinter.Button(self.down_frame, height =40,width = 40, image=self.img_4, padx=10, bg="white")


        #pause button
        self.img_5=Image.open("img\\pause.png")
        self.img_5 = self.img_5.resize((30,30))
        self.img_5=ImageTk.PhotoImage(self.img_5)
        self.pause_button = tkinter.Button(self.down_frame, height =40,width = 40, image=self.img_5, padx=10, bg="white")


        #continue button
        self.img_6=Image.open("img\\continue.png")
        self.img_6 = self.img_6.resize((30,30))
        self.img_6=ImageTk.PhotoImage(self.img_6)
        self.continue_button = tkinter.Button(self.down_frame, height =40,width = 40, image=self.img_6, padx=10, bg="white")


        #stop button
        self.img_7=Image.open("img\\stop.png")
        self.img_7 = self.img_7.resize((30,30))
        self.img_7=ImageTk.PhotoImage(self.img_7)
        self.stop_button = tkinter.Button(self.down_frame, height =40,width = 40, image=self.img_7, padx=10, bg="white")

        # seek bar
        self.seek= tkinter.Scale(self.down_frame, from_=0, to =100, orient="horizontal")

        # Volume slider
        self.volume= tkinter.Scale(self.down_frame, from_=0, to =100, orient="horizontal")

        #refresh to put everythign in place
        self.refresh()

    def refresh(self):
        #frames
        self.left_frame.grid(row=0, column=0, padx=1, pady=1,sticky="nsew")
        self.right_frame.grid(row=0, column=1, padx=0, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.down_frame.grid(row=1, column=0,columnspan=3, padx=0, pady=1, sticky="nsew")
        print(self.grid_size())

        #listbox
        self.listbox.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        #scrollbar
        self.my_scrollbar.grid(row=0, column=1, sticky="ns")

        #Images
        self.app_image.grid(row=0,column=0,sticky="nsew")
        self.play_button.grid(row=0,column=2, sticky="s")
        self.prev_button.grid(row=0,column=1, sticky="s")
        self.next_button.grid(row=0,column=3, sticky="s")
        self.pause_button.grid(row=0,column=4, sticky="s")
        self.continue_button.grid(row=0,column=5, sticky="s")
        self.stop_button.grid(row=0,column=6, sticky="s")

        #seek bar
        self.seek.grid(row=0, column=7)

        #volume slider
        self.volume.grid(row=0, column=8)


    def configure_frames(self):
        self.grid_rowconfigure(0, weight=1)  # Allow the top row (containing left and right frames) to expand vertically
        self.grid_columnconfigure(0, weight=1)  # Allow the first column (containing left frame) to expand horizontally
        self.grid_columnconfigure(1, weight=1)  # Allow the second column (containing right frame) to expand horizontally
        self.grid_rowconfigure(1, weight=1)  # Allow the bottom row (containing down frame) to expand vertically


#configure_frames()  # Call the configure_frames function to make the frames resizable
Window().mainloop()
# #mixer.music.pause() - this is how to pause the music
# #mixer.music.unpause() - this is how to unpause the music
