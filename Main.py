# todo
# add a textbox for the song info above the seek bar
# adjust seek bar to have a max length of the song's max length
# give the pause/play buttons functionality


import tkinter
from tkinter import ttk
from functools import partial
from PIL import ImageTk,Image
import json
import eyed3
import pygame
import os 

# def testChangeSettings():
#   # Changing settings
#   new_settings = {
#       "visual_theme": "dark",
#       "audio_settings": {
#           "volume": 75,
#           "equalizer": {
#               "bass": 2,
#               "treble": -1
#           }
#       },
#       "preferences": {
#           "language": "French",
#           "notifications": False
#       }
#   }

  # Apply the new settings
  #change_settings(new_settings)

  # Save the updated settings
  #save_settings(current_settings)

# directory = "C:/Users/mteag/Music/4K YouTube to MP3/Carry On.mp3"

class Window(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry('1450x800')
        self.configure(background = "white")
        #self.state('zoomed')
        self.buttonImages = {}
        self.buttons = {}
        self.canvases = {}
        self.frames = {}
        self.directory = "C:\\Users\\nicor\\Nico's_Stuff\\NicoCode\\MP3Project\\music" # this is jsut for development, change this later
        self.songs = []
        self.idCounter = 0
        # default settings dictionary
        self.DEFAULT_SETTINGS = {
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
        
        #Load settings at the beginning of your program
        self.current_settings = self.load_settings()

        # Access and update settings as needed
        self.visual_theme = self.current_settings["visual_theme"]
        self.liked_songs = self.current_settings["liked_songs"]
        self.username = self.current_settings["account_info"]["username"]
        self.volume = self.current_settings["audio_settings"]["volume"]
        self.bass = self.current_settings["audio_settings"]["equalizer"]["bass"]
        self.treble = self.current_settings["audio_settings"]["equalizer"]["treble"]
        self.language = self.current_settings["preferences"]["language"]
        self.notifications = self.current_settings["preferences"]["notifications"]
        self.app_version = self.current_settings["about_info"]["version"]
        self.developer = self.current_settings["about_info"]["developer"]
        self.website = self.current_settings["about_info"]["website"]

        #frames
        self.frames["left"] = tkinter.Frame(self,bg = "white")
        self.frames["right"] = tkinter.Frame(self)
        self.frames["down"] = tkinter.Frame(self,bg = "#CFC7F8")


        #stylize the scrollbar with witchcraft and wizardry
        style=ttk.Style()
        style.theme_use('classic')
        style.configure("Vertical.TScrollbar", background="grey", bordercolor="black", arrowcolor="white")

        # Creating a scro1lbar
        self.songScrollbar = ttk.Scrollbar(self.frames["right"], orient="vertical")
        self.songCanvas = tkinter.Canvas(self.frames["right"], yscrollcommand=self.songScrollbar.set,bg = "#333333")
        self.songScrollbar.config(command=self.songCanvas.yview)
        self.songCanvas.bind('<Configure>',lambda e: self.songCanvas.configure(scrollregion=self.songCanvas.bbox("all")))
        self.frames["innerRight"] = tkinter.Frame(self.songCanvas)
        self.songCanvas.create_window((0,0),window=self.frames["innerRight"],anchor="nw")

        #album default icon
        self.genAlbumIcon(2)

        #prev button
        self.genPrevButton(0.4)

        #play button
        self.genPlayButton(0.4)

        #pause button
        self.genPauseButton(0.4)

        #next button
        self.genNextButton(0.4)

        # seek bar
        self.seek= tkinter.Scale(self.frames["down"], from_=0, to =100, orient="horizontal")

        # Volume slider
        self.volume= tkinter.Scale(self.frames["down"], from_=0, to =100, orient="horizontal")

        #refresh to put everythign in place


        self.loadSongs()
        pygame.mixer.init()

        self.refresh()

    #there should be a set directory button for the whole application

    # give this a button
    def loadSongs(self):
        #filepath = input("Enter filepath")
        if os.path.isdir(self.directory):
            os.chdir(self.directory)
            
            fileNames = os.listdir(self.directory) 

            if len(fileNames) == 0: 
                #needs error handling eventually
                print("Folder empty \n")
            else: 
                for i in fileNames:
                    self.idCounter = 0
                    mp3 = eyed3.load(self.directory + "\\" + i)
                    print(mp3)

                    trackTitle = mp3.tag.title
                    trackArtist = mp3.tag.artist
                    trackAlbum = mp3.tag.album
                    trackRD = mp3.tag.getBestDate() 
                    trackImage = False

                    if trackTitle == None: trackTitle = "Unknown"
                    if trackArtist == None: trackArtist = "Unknown"
                    if trackAlbum == None: trackAlbum = "Unknown"
                    if trackRD == None: trackRD = "Unknown"

                    for image in mp3.tag.images:
                        image_file = open(f"..\\imgs\\{self.idCounter} - {trackTitle} - {trackArtist}().jpg","wb+")
                        image_file.write(image.image_data)
                        image_file.close()
                        trackImage = True

                    self.songs.append({"id":self.idCounter,"Title":trackTitle,"Artist":trackArtist,"Album":trackAlbum,"Release":trackRD, "Image":trackImage, "Directory":i})
                    self.idCounter += 1
                self.loadSongsIntoFrame()
        else:
            #needs error handling eventually
            print("File doesn't exist \n")

    def loadSongsIntoFrame(self):
         for i in range(len(self.songs)):
             tkinter.Button(self.frames["innerRight"],text=f"Title: {self.songs[i]['Title']} | Artist: {self.songs[i]['Artist']} | Album: {self.songs[i]['Album']}", command=partial(self.queueSong,self.songs[i]["id"]),bg="black", activebackground="grey", fg="white").grid(row=i,column=0)

    def queueSong(self,id):
        self.songQueued = False
        for i in range(len(self.songs)):
            if self.songs[i]["id"] == id:
                self.songQueued = self.songs[i]
        
        if not self.songQueued == False:
            self.canvasAlbum.delete("all")
            self.canvasAlbum.grid_remove()
            self.canvasAlbum.pack(side = "left", fill = "both", expand = True ,padx=2,pady=2)
            self.albumimg = ImageTk.PhotoImage(Image.open(f"..\\imgs\\{self.songQueued['id']} - {self.songQueued['Title']} - {self.songQueued['Artist']}().jpg"))
            self.canvasAlbum.create_image(0, 0, anchor="nw", image=self.albumimg)
            pygame.mixer.music.load(self.directory + "\\" + self.songQueued["Directory"])
            pygame.mixer.music.play()

    # load settings from the JSON file
    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
        except FileNotFoundError:
            settings = self.DEFAULT_SETTINGS
        return settings

    # Save settings to the JSON file
    def save_settings(self,settings):
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)

    # Function to change settings
    def change_settings(self,new_settings):
        for key, value in new_settings.items():
            if key in self.current_settings:
                self.current_settings[key] = value
            else:
                print(f"Invalid setting: {key}")

    def refresh(self):
        for i in range(len(self.frames)):
            self.frames[list(self.frames)[i]].grid_remove()

        #frames
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=1)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(4,weight=1)
        self.rowconfigure(5,weight=1)
        self.frames["left"].grid(row=0, column=0, padx=1, pady=1,sticky="nsew",rowspan=5)
        self.frames["left"].grid_rowconfigure(0, weight=1)
        self.frames["left"].grid_columnconfigure(0, weight=1)
        self.frames["left"].grid_rowconfigure(1, weight=1)
        self.frames["left"].grid_columnconfigure(1, weight=1)
        self.frames["left"].grid_rowconfigure(2, weight=1)
        self.frames["left"].grid_columnconfigure(2, weight=1)
        self.frames["right"].grid(row=0, column=1, padx=0, sticky="nsew",rowspan=5)
        self.frames["right"].grid_rowconfigure(0, weight=1)
        self.frames["right"].grid_columnconfigure(0, weight=1)
        self.frames["down"].grid(row=5, column=0,columnspan=2, padx=0, pady=1, sticky="nsew")
        self.songCanvas.grid(row=0,column=0,sticky="nsew")
        self.songCanvas.grid_rowconfigure(0,weight=1)
        self.songCanvas.grid_columnconfigure(0,weight=1)

        #scrollbar
        self.songScrollbar.grid(row=0, column=1, sticky="nsew")

        #Images
        self.refreshCanvases()

        #seek bar
        self.seek.grid(row=0, column=0,columnspan=7,sticky="nsew")

        #volume slider
        self.volume.grid(row=0, column=7,columnspan=3,sticky="nsew")

        #makes all of the frames expand to fit the window
        #parent window
        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i,weight=1)
        for i in range(self.grid_size()[1]):
            self.grid_rowconfigure(i,weight=1)

    def refreshCanvases(self):
        self.canvasAlbum.grid_remove()
        for i in range(len(self.canvases)):
            self.canvases[list(self.canvases)[i]].grid_remove()
        
        self.canvasAlbum.grid(row=1,column=1)
        for i in range(len(self.canvases)):
            self.canvases[list(self.canvases)[i]].grid(row=1,column=i,pady=2)

    #generates the play button image
    def genPlayButton(self,factor):
        self.canvases["play"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["play"].create_oval(10*factor,10*factor,97*factor,97*factor, outline="black", fill="white", width=2)
        self.canvases["play"].create_polygon([40*factor,25*factor,80*factor,50*factor,40*factor,80*factor],outline="black",fill="white",width=2)
        #the function for clicking on the play button (just animation right now)
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_oval(10*factor+2,10*factor+2,97*factor+2,97*factor+2, outline="black", fill="white", width=2)
            event.widget.create_polygon([40*factor+2,25*factor+2,80*factor+2,50*factor+2,40*factor+2,80*factor+2],outline="black",fill="white",width=2)
        self.canvases["play"].bind("<ButtonPress-1>",onClick)
        #the function for releasing the play button (just animation right now)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_oval(10*factor,10*factor,97*factor,97*factor, outline="black", fill="white", width=2)
            event.widget.create_polygon([40*factor,25*factor,80*factor,50*factor,40*factor,80*factor],outline="black",fill="white",width=2)
            self.play()
        self.canvases["play"].bind("<ButtonRelease-1>",onRelease)

    def genPauseButton(self,factor):
        self.canvases["pause"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["pause"].create_rectangle(23*factor,10*factor,43*factor,95*factor, outline="black", fill="white", width=2)
        self.canvases["pause"].create_rectangle(65*factor,10*factor,85*factor,95*factor, outline="black", fill="white", width=2)
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_rectangle(23*factor+2,10*factor+2,43*factor+2,95*factor+2, outline="black", fill="white", width=2)
            event.widget.create_rectangle(65*factor+2,10*factor+2,85*factor+2,95*factor+2, outline="black", fill="white", width=2)
        self.canvases["pause"].bind("<ButtonPress-1>",onClick)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_rectangle(23*factor,10*factor,43*factor,95*factor, outline="black", fill="white", width=2)
            event.widget.create_rectangle(65*factor,10*factor,85*factor,95*factor, outline="black", fill="white", width=2)
            self.pause()
        self.canvases["pause"].bind("<ButtonRelease-1>",onRelease)

    def genNextButton(self,factor):
        self.canvases["next"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["next"].create_polygon([20*factor,25*factor,60*factor,50*factor,20*factor,80*factor],outline="black",fill="white",width=2)
        self.canvases["next"].create_rectangle(75*factor,25*factor,85*factor,80*factor,outline="black",fill="white",width=2)
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_polygon([20*factor+2,25*factor+2,60*factor+2,50*factor+2,20*factor+2,80*factor+2],outline="black",fill="white",width=2)
            event.widget.create_rectangle(75*factor+2,25*factor+2,85*factor+2,80*factor+2,outline="black",fill="white",width=2)
        self.canvases["next"].bind("<ButtonPress-1>",onClick)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_polygon([20*factor,25*factor,60*factor,50*factor,20*factor,80*factor],outline="black",fill="white",width=2)
            event.widget.create_rectangle(75*factor,25*factor,85*factor,80*factor,outline="black",fill="white",width=2)
        self.canvases["next"].bind("<ButtonRelease-1>",onRelease)

    def genPrevButton(self,factor):
        self.canvases["prev"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["prev"].create_polygon([85*factor,25*factor,45*factor,50*factor,85*factor,80*factor],outline="black",fill="white",width=2)
        self.canvases["prev"].create_rectangle(20*factor,25*factor,30*factor,80*factor,outline="black",fill="white",width=2)
        self.canvases["prev"].grid(row=0,column=0)
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_polygon([85*factor+2,25*factor+2,45*factor+2,50*factor+2,85*factor+2,80*factor+2],outline="black",fill="white",width=2)
            event.widget.create_rectangle(20*factor+2,25*factor+2,30*factor+2,80*factor+2,outline="black",fill="white",width=2)
        self.canvases["prev"].bind("<ButtonPress-1>",onClick)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_polygon([85*factor,25*factor,45*factor,50*factor,85*factor,80*factor],outline="black",fill="white",width=2)
            event.widget.create_rectangle(20*factor,25*factor,30*factor,80*factor,outline="black",fill="white",width=2)
        self.canvases["prev"].bind("<ButtonRelease-1>",onRelease)
    
    def genAlbumIcon(self,factor):
        self.canvasAlbum = tkinter.Canvas(self.frames["left"],width=100*factor,height=100*factor,background="grey")
        self.canvasAlbum.create_oval(35*factor,20*factor,65*factor,50*factor,outline="black",fill="white",width=2)
        self.canvasAlbum.create_polygon([30*factor,60*factor,70*factor,60*factor,80*factor,70*factor,80*factor,80*factor,20*factor,80*factor,20*factor,70*factor,30*factor,60*factor],outline="black",fill="white",width=2)

    def play(self):
        pygame.mixer.music.unpause()

    def pause(self):
        pygame.mixer.music.pause()

#configure_frames()  # Call the configure_frames function to make the frames resizable
Window().mainloop()
# #mixer.music.pause() - this is how to pause the music
# #mixer.music.unpause() - this is how to unpause the music
