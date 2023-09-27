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

def playSong(directory):
    mixer.init()
    mixer.music.load(directory)
    mixer.music.play()

# #mixer.music.pause() - this is how to pause the music
# #mixer.music.unpause() - this is how to unpause the music
