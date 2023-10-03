# todo
# add a textbox for the song info above the seek bar
# investigate the mixer channel stuff to see if it can do crossfade

import time, tkinter, json, eyed3, pygame, os, threading
from tkinter import ttk
from functools import partial
from PIL import ImageTk,Image

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
        self.paused = False
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
        self.seek= tkinter.Scale(self.frames["down"], from_=0, to =100, orient="horizontal",command=self.seekTo)
        self.songQueued = {"id":None,"Title":None,"Artist":None,"Album":None,"Release":None, "Image":None, "Directory":None,"Length":0}
        self.mixer = pygame.mixer
        self.mixer.init()
        self.seekUpdater = self.updateSeek(self)
        self.seekUpdater.start()
        self.protocol("WM_DELETE_WINDOW",self.tidyDestroy)

        # Volume slider
        self.volume= tkinter.Scale(self.frames["down"], from_=0, to =100, orient="horizontal", command=self.setVolume)
        self.volume.set(100)

        #refresh to put everythign in place


        self.loadSongs()

        self.refresh()

    #there should be a set directory button for the whole application

    # give this a button
    def loadSongs(self):
        #filepath = input("Enter filepath")

        if os.path.isdir(self.directory):
            os.chdir(self.directory)

            #this resets the imgs folder so that it's a fresh start
            if os.path.exists("..\\imgs"): 
                os.chdir("..\\imgs")
                for i in os.listdir():
                    os.remove(str(os.getcwd()) + "\\" + str(i))
                    
                os.chdir(self.directory)

            fileNames = os.listdir(self.directory) 

            if len(fileNames) == 0: 
                #needs error handling eventually
                print("Folder empty \n")
            else: 
                for i in fileNames:
                    mp3 = eyed3.load(self.directory + "\\" + i)

                    trackTitle = mp3.tag.title
                    trackArtist = mp3.tag.artist
                    trackAlbum = mp3.tag.album
                    trackRD = mp3.tag.getBestDate() 
                    trackImage = False

                    if trackTitle == None: trackTitle = "Unknown"
                    if trackArtist == None: trackArtist = "Unknown"
                    if trackAlbum == None: trackAlbum = "Unknown"
                    if trackRD == None: trackRD = "Unknown"

                    #this generates the imgs from the mp3s
                    for image in mp3.tag.images:
                        image_file = open(f"..\\imgs\\{self.idCounter} - {trackTitle} - {trackArtist}().jpg","wb+")
                        image_file.write(image.image_data)
                        image_file.close()
                        trackImage = True

                    self.songs.append({"id":self.idCounter,"Title":trackTitle,"Artist":trackArtist,"Album":trackAlbum,"Release":trackRD, "Image":trackImage, "Directory":i,"Length":mp3.info.time_secs})
                    self.idCounter += 1
                self.loadSongsIntoFrame()
        else:
            #needs error handling eventually
            print("File doesn't exist \n")

    #loads songs into the right frame tkinter frame
    def loadSongsIntoFrame(self):
         for i in range(len(self.songs)):
             tkinter.Button(self.frames["innerRight"],text=f"Title: {self.songs[i]['Title']} | Artist: {self.songs[i]['Artist']} | Album: {self.songs[i]['Album']}", command=partial(self.queueSong,self.songs[i]["id"]),bg="black", activebackground="grey", fg="white").grid(row=i,column=0)

    #queues and plays the selected song
    def queueSong(self,id):
        for i in range(len(self.songs)):
            if self.songs[i]["id"] == id:
                self.songQueued = self.songs[i]
        
        #verifies the song exists and was loaded
        if not self.songQueued["id"] == None:
            #resets and fills the left frame's canvas with the album cover
            self.canvasAlbum.delete("all")
            self.canvasAlbum.grid_remove()
            self.canvasAlbum.pack(side = "left", fill = "both", expand = True ,padx=2,pady=2)
            self.albumimg = ImageTk.PhotoImage(Image.open(f"..\\imgs\\{self.songQueued['id']} - {self.songQueued['Title']} - {self.songQueued['Artist']}().jpg"))
            self.canvasAlbum.create_image(0, 0, anchor="nw", image=self.albumimg)
            #gives the seek abr the right length
            self.seek.config(to=self.songQueued["Length"])
            #sets the seek bar back to 0
            self.seek.set(0)
            #loads and then plays the selected song
            self.mixer.music.load(self.directory + "\\" + self.songQueued["Directory"])
            self.mixer.music.play()

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
    
    #a thread to update the seek bar every second
    class updateSeek(threading.Thread):
        def __init__(self,parent):
            super().__init__()
            self.parent = parent
            self._stop = threading.Event()
            self.daemon = True

        def run(self):
            while not self._stop.is_set():
                if not self.parent.seek.get() == self.parent.songQueued["Length"] and not self.parent.paused:
                    self.parent.seek.set(self.parent.seek.get() + 1)
                time.sleep(1)
            return

    # a fresh function for all of the elements on the page (tkinter thing)
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
        for i in range(7):
            self.frames["down"].grid_columnconfigure(i, weight=1)
        self.frames["down"].grid_rowconfigure(0, weight=1)
        self.frames["down"].grid_rowconfigure(1, weight=1)

        #scrollbar
        self.songScrollbar.grid(row=0, column=1, sticky="nsew")

        #Images
        self.refreshCanvases()

        #seek bar
        self.seek.grid(row=0, column=0,columnspan=4,sticky="nsew")
        

        #volume slider
        self.volume.grid(row=0, column=4,columnspan=3,sticky="nsew")

        #makes all of the frames expand to fit the window
        #parent window
        for i in range(self.grid_size()[0]):
            self.grid_columnconfigure(i,weight=1)
        for i in range(self.grid_size()[1]):
            self.grid_rowconfigure(i,weight=1)

    # a refresh for only the canvases (buttons and album cover)
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
        #the function for clicking on the play button
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_oval(10*factor+2,10*factor+2,97*factor+2,97*factor+2, outline="black", fill="white", width=2)
            event.widget.create_polygon([40*factor+2,25*factor+2,80*factor+2,50*factor+2,40*factor+2,80*factor+2],outline="black",fill="white",width=2)
        self.canvases["play"].bind("<ButtonPress-1>",onClick)
        #the function for releasing the play button (actually plays)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_oval(10*factor,10*factor,97*factor,97*factor, outline="black", fill="white", width=2)
            event.widget.create_polygon([40*factor,25*factor,80*factor,50*factor,40*factor,80*factor],outline="black",fill="white",width=2)
            self.play()
        self.canvases["play"].bind("<ButtonRelease-1>",onRelease)

    #generates the pause button image
    def genPauseButton(self,factor):
        self.canvases["pause"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["pause"].create_rectangle(23*factor,10*factor,43*factor,95*factor, outline="black", fill="white", width=2)
        self.canvases["pause"].create_rectangle(65*factor,10*factor,85*factor,95*factor, outline="black", fill="white", width=2)
        # function for pressing the pause button
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_rectangle(23*factor+2,10*factor+2,43*factor+2,95*factor+2, outline="black", fill="white", width=2)
            event.widget.create_rectangle(65*factor+2,10*factor+2,85*factor+2,95*factor+2, outline="black", fill="white", width=2)
        self.canvases["pause"].bind("<ButtonPress-1>",onClick)
        #function for releasing the pause button (actually pauses)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_rectangle(23*factor,10*factor,43*factor,95*factor, outline="black", fill="white", width=2)
            event.widget.create_rectangle(65*factor,10*factor,85*factor,95*factor, outline="black", fill="white", width=2)
            self.pause()
        self.canvases["pause"].bind("<ButtonRelease-1>",onRelease)

    #generates the next button
    def genNextButton(self,factor):
        self.canvases["next"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["next"].create_polygon([20*factor,25*factor,60*factor,50*factor,20*factor,80*factor],outline="black",fill="white",width=2)
        self.canvases["next"].create_rectangle(75*factor,25*factor,85*factor,80*factor,outline="black",fill="white",width=2)
        #function for clicking the next button
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_polygon([20*factor+2,25*factor+2,60*factor+2,50*factor+2,20*factor+2,80*factor+2],outline="black",fill="white",width=2)
            event.widget.create_rectangle(75*factor+2,25*factor+2,85*factor+2,80*factor+2,outline="black",fill="white",width=2)
        self.canvases["next"].bind("<ButtonPress-1>",onClick)
        #function for releasing the next button (actually moves to the next song)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_polygon([20*factor,25*factor,60*factor,50*factor,20*factor,80*factor],outline="black",fill="white",width=2)
            event.widget.create_rectangle(75*factor,25*factor,85*factor,80*factor,outline="black",fill="white",width=2)
            self.moveSong(1)
        self.canvases["next"].bind("<ButtonRelease-1>",onRelease)

    #generates the previous button
    def genPrevButton(self,factor):
        self.canvases["prev"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["prev"].create_polygon([85*factor,25*factor,45*factor,50*factor,85*factor,80*factor],outline="black",fill="white",width=2)
        self.canvases["prev"].create_rectangle(20*factor,25*factor,30*factor,80*factor,outline="black",fill="white",width=2)
        self.canvases["prev"].grid(row=0,column=0)
        #function for pressing the previous button
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            event.widget.create_polygon([85*factor+2,25*factor+2,45*factor+2,50*factor+2,85*factor+2,80*factor+2],outline="black",fill="white",width=2)
            event.widget.create_rectangle(20*factor+2,25*factor+2,30*factor+2,80*factor+2,outline="black",fill="white",width=2)
        self.canvases["prev"].bind("<ButtonPress-1>",onClick)
        #function for releasing the previous button (actually moves to the previous song)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            event.widget.create_polygon([85*factor,25*factor,45*factor,50*factor,85*factor,80*factor],outline="black",fill="white",width=2)
            event.widget.create_rectangle(20*factor,25*factor,30*factor,80*factor,outline="black",fill="white",width=2)
            self.moveSong(-1)
        self.canvases["prev"].bind("<ButtonRelease-1>",onRelease)
    
    #generates the default album icon for a placeholder on startup
    def genAlbumIcon(self,factor):
        self.canvasAlbum = tkinter.Canvas(self.frames["left"],width=100*factor,height=100*factor,background="grey")
        self.canvasAlbum.create_oval(35*factor,20*factor,65*factor,50*factor,outline="black",fill="white",width=2)
        self.canvasAlbum.create_polygon([30*factor,60*factor,70*factor,60*factor,80*factor,70*factor,80*factor,80*factor,20*factor,80*factor,20*factor,70*factor,30*factor,60*factor],outline="black",fill="white",width=2)

    #play function
    def play(self):
        self.mixer.music.unpause()
        self.paused = False

    #pause function
    def pause(self):
        self.mixer.music.pause()
        self.paused = True

    #seeking function to move the song to reflect the time shown on the seek bar
    def seekTo(self,event):
        #logic to handle if it's paused or not nad if it's playing or not
        if not self.mixer.music.get_busy() and not self.paused:
            self.mixer.music.play()
            self.mixer.music.set_pos(self.seek.get())
        else:
            self.mixer.music.set_pos(self.seek.get())

    #the volume setting function for the volume slider
    def setVolume(self,event):
        self.mixer.music.set_volume(self.volume.get()/100)

    #the is run on the X being clicked so that the threads are properly shut down with the window
    def tidyDestroy(self):
        self.seekUpdater._stop.set
        time.sleep(1)
        self.destroy()

    #this is the function for the next and previous buttons
    def moveSong(self,direction):
        if -1 < self.songQueued["id"] + direction < len(self.songs):
            self.queueSong(self.songs[self.songQueued["id"] + direction]["id"])
        elif self.songQueued["id"] + direction <= -1:
            self.queueSong(self.songs[len(self.songs)-1]["id"])
        elif self.songQueued["id"] + direction > len(self.songs)-1:
            self.queueSong(self.songs[0]["id"])

# this runs the whole file
Window().mainloop()