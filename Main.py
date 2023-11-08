# todo
# add a textbox for the song info above the seek bar
# investigate the mixer channel stuff to see if it can do crossfade
# click on seek to move it to that position
# optimization?
# finding its own directory


import time, tkinter, json, eyed3, pygame, os, threading
from tkinter import ttk
from tkinter import filedialog
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

new_directory = "MP3_App"
home_directory = os.path.expanduser ("~")
music_directory = os.path.join(home_directory, "Music")

music_directory_path = os.path.join(music_directory, new_directory)

if not os.path.exists(music_directory_path): 
    os.makedirs(music_directory_path)

class Window(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry('1450x800')
        self.configure(background = "gray")
        self.buttonImages = {}
        self.buttons = {}
        self.canvases = {}
        self.frames = {}
        self.directory = music_directory_path
        self.songs = []
        self.songButtons = []
        self.idCounter = 0
        self.paused = True
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
        self.frames["down"] = tkinter.Frame(self,bg = "#7aa7f0")

        #stylize the scrollbar with witchcraft and wizardry
        style=ttk.Style()
        style.theme_use('classic')
        style.configure("Vertical.TScrollbar", background="grey", bordercolor="black", arrowcolor="white")

        #album default icon
        self.genAlbumIcon(2)

        #prev button
        self.genPrevButton(0.4)

        #play button
        self.genPausePlayButton(0.4)

        #next button
        self.genNextButton(0.4)

         #QueueListbox
        self.createListbox()
        #Listbox buttons
        self.buttonListbox()

        # seek bar
        self.seek= tkinter.Scale(self.frames["down"], from_=0, to =0, orient="horizontal", label="00:00", showvalue=0, command=self.moveSeek)
        self.seek.bind("<ButtonRelease-1>",self.seekTo)
        self.songQueued = {"id":None,"Title":None,"Artist":None,"Album":None,"Release":None, "Image":None, "Directory":None,"Length":0}
        self.mixer = pygame.mixer
        self.seekUpdater = self.updateSeek(self)
        self.seekUpdater.start()
        self.protocol("WM_DELETE_WINDOW",self.tidyDestroy)
        self.mixer.init()    

        # Volume slider
        self.volume= tkinter.Scale(self.frames["down"], from_=0, to =100, orient="horizontal", command=self.setVolume, label="Volume")
        self.volume.set(50)

        #tag information stuff
        self.tagInfo = tkinter.Label(self.frames["down"],font=("Roboto Mono",14))
        #refresh to put everything in place

        # Allows the user to select a directory and automatically update the list in the application
        def select_directory():
            self.directory = filedialog.askdirectory() 
            self.removeButtons()          
            self.refresh() 
            self.ListboxRemoveOldSongs()
            self.loadSongs()
            self.songScrollbar.update()
            self.ListboxHighlightPlaying()

        tkinter.Button(self.frames["down"], text = "Select Directory", command = select_directory,bg="SystemButtonFace", activebackground="Black", fg="Black").grid(row=5, column=0)
        
        # refresh to put everything in place
        self.refresh()
        self.loadSongs()

    #there should be a set directory button for the whole application
# Search bar and search button
        self.search_entry = tkinter.Entry(self.frames["down"], width=20)
        self.search_entry.grid(row=0, column=7, padx=5)
        self.search_button = tkinter.Button(self.frames["down"], text="Search", command=self.search_song)
        self.search_button.grid(row=0, column=8, padx=5)

        # Search results listbox
        self.search_results = tkinter.Listbox(self.frames["down"], selectmode=tkinter.SINGLE, height=10)
        self.search_results.grid(row=1, column=7, columnspan=2, padx=5)
        self.search_results.bind("<<ListboxSelect>>", self.select_song)

        # Update the search results
        self.filtered_songs = []
        self.update_search_results()

    def search_song(self):
        query = self.search_entry.get().strip().lower()
        if query:
            self.filtered_songs = [song for song in self.songs if query in song["Title"].lower()]
        else:
            self.filtered_songs = self.songs
        self.update_search_results()

    def update_search_results(self):
        self.search_results.delete(0, tkinter.END)
        for song in self.filtered_songs:
            self.search_results.insert(tkinter.END, f"{song['Title']} - {song['Artist']}")

    def select_song(self, event):
        selected_index = self.search_results.curselection()
        if selected_index:
            selected_song = self.filtered_songs[int(selected_index[0])]
            self.queueSong(selected_song["id"])

    # give this a button
    def loadSongs(self):
        self.songs = []
        self.idCounter = 0
        #filepath = input("Enter filepath")

        if os.path.isdir(self.directory):
            os.chdir(self.directory)
              
            self.songs.clear()

            #this resets the imgs folder so that it's a fresh start
            if not os.path.exists("..\\imgs"): os.mkdir("..\\imgs")
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
                    if i.lower().endswith(".mp3"):
                        mp3 = eyed3.load(self.directory + "\\" + i)

                        if mp3:
                            trackTitle = mp3.tag.title
                            trackArtist = mp3.tag.artist
                            trackAlbum = mp3.tag.album
                            trackRD = mp3.tag.getBestDate()
                            trackImage = False
                        else:
                            print("Error loading MP3")

                        # if trackTitle == None: trackTitle = "Unknown"
                        # if trackArtist == None: trackArtist = "Unknown"
                        # if trackAlbum == None: trackAlbum = "Unknown"
                        # if trackRD == None: trackRD = "Unknown"

                        #this generates the imgs from the mp3s
                        if mp3.tag.images:
                            for image in mp3.tag.images:
                                image_file = open(f"..\\imgs\\{self.idCounter} - {trackTitle} - {trackArtist}().jpg","wb+")
                                image_file.write(image.image_data)
                                image_file.close()
                                trackImage = True
                        else:
                            self.canvasAlbum.delete("all")
                            self.canvasAlbum.grid_remove()
                            self.canvasAlbum.grid(row=1,column=1)
                            # self.canvasAlbum.pack(side = "left", fill = "both", expand = True ,padx=2,pady=2)
                            self.genAlbumIcon(2)
                            trackImage = False

                        #This append function prevents the program from loading mp3 files that have no image, because each ID in the array must include a value for trackImage
                        self.songs.append({"id":self.idCounter,"Title":trackTitle,"Artist":trackArtist,"Album":trackAlbum,"Release":trackRD,"Image":trackImage,"Directory":i,"Length":mp3.info.time_secs})
                        # print(mp3.info.time_secs, end = " | ")
                        self.idCounter += 1
                self.loadSongsIntoFrame()
                self.queueSong(self.songs[0]["id"])                
        else:
            #needs error handling eventually
            print("File doesn't exist \n")

    #loads songs into the right frame tkinter frame
    def loadSongsIntoFrame(self):
        for i in range(len(self.songs)):
            button_text = f"Title: {self.songs[i]['Title']} | Artist: {self.songs[i]['Artist']} | Album: {self.songs[i]['Album']}"
            songButton = tkinter.Button(self.frames["innerRight"], text=button_text, command=partial(self.queueSong, self.songs[i]["id"]), bg="black", activebackground="grey", fg="white")
            songButton.grid(row=i, column=0)
            self.songButtons.append(songButton)

    def removeButtons(self):
        self.songCanvas.delete("all")
        self.songScrollbar.destroy()
        self.frames["innerRight"] = tkinter.Frame(self.songCanvas)
        self.songCanvas.create_window((0,0),window=self.frames["innerRight"],anchor="nw")
        # self.songButtons = []
        # pass

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
            #displays information about the currently playing track
            self.tagInfo.config(text=f"{self.songQueued['Title']}   |   {self.songQueued['Artist']}   |   {self.songQueued['Album']}")
            self.seek.config(label="00:00")
            #loads and then plays the selected song
            self.mixer.music.load(self.directory + "\\" + self.songQueued["Directory"])
            self.mixer.music.play()
            if self.paused: self.pause()
            self.loadIntoListbox()

    # load settings from the JSON file
    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
        except FileNotFoundError:
            settings = self.DEFAULT_SETTINGS
        return settings
    
    def genScrollBar(self):
        # Creating a scro1lbar
        self.songScrollbar = ttk.Scrollbar(self.frames["right"], orient="vertical")
        self.songCanvas = tkinter.Canvas(self.frames["right"], yscrollcommand=self.songScrollbar.set,bg = "#333333")
        self.songScrollbar.config(command=self.songCanvas.yview)
        self.songCanvas.bind('<Configure>',lambda e: self.songCanvas.configure(scrollregion=self.songCanvas.bbox("all")))
        self.frames["innerRight"] = tkinter.Frame(self.songCanvas)
        self.songCanvas.create_window((0,0),window=self.frames["innerRight"],anchor="nw")

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

        self.genScrollBar()

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
            self.frames["down"].grid_columnconfigure(i, weight=1,uniform="column")
        for i in range(6):
            self.frames["down"].grid_rowconfigure(i, weight=1)
        

        #scrollbar
        self.songScrollbar.grid(row=0, column=1, sticky="nsew")

        #tag info
        self.tagInfo.grid(row=0,column=0,columnspan=7, sticky="nsew")

        #Images
        self.refreshCanvases()

        #seek bar
        self.seek.grid(row=1, column=0,columnspan=4,sticky="nsew")
        
        #volume slider
        self.volume.grid(row=1, column=4,columnspan=3,sticky="nsew")

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
            self.canvases[list(self.canvases)[i]].grid(row=2,column=i,pady=2)

    #generates the play/pause button image
    def genPausePlayButton(self,factor):
        self.canvases["play"] = tkinter.Canvas(self.frames["down"],width=100*factor,height=100*factor,background="SystemButtonFace",borderwidth=2,relief="raised")
        self.canvases["play"].create_oval(10*factor,10*factor,97*factor,97*factor, outline="black", fill="white", width=2)
        self.canvases["play"].create_polygon([40*factor,25*factor,80*factor,50*factor,40*factor,80*factor],outline="black",fill="white",width=2)
        #the function for clicking on the play button
        def onClick(event):
            event.widget.configure(relief="sunken")
            event.widget.delete("all")
            if self.paused:
                event.widget.create_oval(10*factor+2,10*factor+2,97*factor+2,97*factor+2, outline="black", fill="white", width=2)
                event.widget.create_polygon([40*factor+2,25*factor+2,80*factor+2,50*factor+2,40*factor+2,80*factor+2],outline="black",fill="white",width=2)
            else:
                event.widget.create_rectangle(23*factor+2,10*factor+2,43*factor+2,95*factor+2, outline="black", fill="white", width=2)
                event.widget.create_rectangle(65*factor+2,10*factor+2,85*factor+2,95*factor+2, outline="black", fill="white", width=2)
        self.canvases["play"].bind("<ButtonPress-1>",onClick)
        #the function for releasing the play button (actually plays)
        def onRelease(event):
            event.widget.configure(relief="raised")
            event.widget.delete("all")
            if not self.paused:
                event.widget.create_oval(10*factor,10*factor,97*factor,97*factor, outline="black", fill="white", width=2)
                event.widget.create_polygon([40*factor,25*factor,80*factor,50*factor,40*factor,80*factor],outline="black",fill="white",width=2)
                self.pause()
            else:
                event.widget.create_rectangle(23*factor,10*factor,43*factor,95*factor, outline="black", fill="white", width=2)
                event.widget.create_rectangle(65*factor,10*factor,85*factor,95*factor, outline="black", fill="white", width=2)
                self.play()
        self.canvases["play"].bind("<ButtonRelease-1>",onRelease)

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
            self.ListboxHighlightPlaying()
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

            if (self.seek.get() <= 5):
                self.moveSong(-1)
                self.ListboxHighlightPlaying()
            else:
                self.seek.set(0)
                self.mixer.music.set_pos(self.seek.get())

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
        self.seek.config(label=f"{int(self.seek.get() / 60):02d}:{int((float(self.seek.get() / 60) - int(self.seek.get() / 60)) * 60 ):02d}")
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
        currentSong = self.songQueued
        for index, song in enumerate(self.songs):
            if song["id"]== currentSong["id"]:
                break
        
        if direction == -1:
            if index == 0:
                self.queueSong(self.songs[len(self.songs)-1]["id"])
            else:
                self.queueSong(self.songs[index-1]["id"])
        if direction == 1:
            if index == len(self.songs)-1:
                self.queueSong(self.songs[0]["id"])
            else:
                self.queueSong(self.songs[index + 1]["id"])
        #old function
        #if -1 < self.songQueued["id"] + direction < len(self.songs):
         #   self.queueSong(self.songs[self.songQueued["id"] + direction]["id"])
    # This is code I tried to add  
          
      #  elif self.songQueued["id"] + direction <= -1:
       #     self.queueSong(self.songs[len(self.songs)-1]["id"])
       # elif self.songQueued["id"] + direction > len(self.songs)-1:
       #     self.queueSong(self.songs[0]["id"])
            
    def moveSeek(self, event):
        self.seek.config(label=f"{int(self.seek.get() / 60):02d}:{int((float(self.seek.get() / 60) - int(self.seek.get() / 60)) * 60 ):02d}")
        if self.seek.get() == int(self.songQueued["Length"]) and not self.paused:
            self.moveSong(1)
            self.ListboxHighlightPlaying()

       #Favorites
            self.favorites=[]
            self.load_favorites()
            self.load_songs()
            self.refresh ()

           # Add this function to toggle favorites


    def toggle_favorite(self, track_id):
        if track_id in self.favorites:
            self.favorites.remove(track_id)
        else:
            self.favorites.append(track_id)

        # Update the "Favorites" playlist in the UI.
        self.update_favorites_playlist()

        # Save favorites to settings.
        self.save_favorites()
    
 
    def update_favorites_playlist(self):
    # Clear the current favorites playlist (if any).
        self.frames["favorites"].destroy()

        # Create a new frame for the "Favorites" playlist.
        self.frames["favorites"] = tkinter.Frame(self, bg="white")
        self.frames["favorites"].grid(row=0, column=1, padx=1, pady=1, sticky="nsew", rowspan=5)
        self.frames["favorites"].grid_rowconfigure(0, weight=1)
        self.frames["favorites"].grid_columnconfigure(0, weight=1)

        # Add a label to the "Favorites" playlist.
        tkinter.Label(self.frames["favorites"], text="Favorites Playlist", bg="white").grid(row=0, column=0, padx=5, pady=5)



        # Add favorited tracks to the "Favorites" playlist.
        for track in self.songs:
            if track["id"] in self.favorites:
                tkinter.Button(self.frames["favorites"], text=f"Title: {track['Title']} | Artist: {track['Artist']} | Album: {track['Album']}",
                            command=partial(self.queueSong, track["id"]), bg="black", activebackground="grey", fg="white").grid(row=track["id"] + 1, column=0)
    

        def load_songs(self):
            self.songs = []
            self.idCounter = 0


        for i in range(len(self.songs)):
            # Create a "Favorite" button for each song
            fav_button = tkinter.Button(self.frames["innerRight"], text=f"Title: {self.songs[i]['Title']} | Artist: {self.songs[i]['Artist']} | Album: {self.songs[i]['Album']}",
                            command=partial(self.queueSong, self.songs[i]["id"]), bg="black", activebackground="grey", fg="white")
            
            # Create a function to toggle favorites when the button is clicked
            fav_button.configure(command=partial(self.toggle_favorite, self.songs[i]["id"]))
            
            fav_button.grid(row=i, column=0)
            self.songButtons.append(fav_button)


    def createListbox(self):
        self.listbox_scrollbar = tkinter.Scrollbar(self.frames["down"],orient = "vertical")
        self.Queue_listbox = tkinter.Listbox(self.frames["down"], bg = "white", yscrollcommand=self.listbox_scrollbar.set)   
       # self.Queue_listbox.insert(tkinter.END, "SongQueue")
        self.Queue_listbox.config(yscrollcommand=self.listbox_scrollbar.set)        
        self.listbox_scrollbar.config(command=self.Queue_listbox.yview)
        self.Queue_listbox.grid(row=2, column =3,rowspan=2, sticky ="nsew") 
        self.listbox_scrollbar.grid(row=2, column=4,rowspan=2,sticky="nsw")   

    def loadIntoListbox(self):
        #Populates the listbox 
        listbox_items = self.Queue_listbox.get(0,tkinter.END)
        for song in self.songs:
            song_key = f"{song['id']}: {song['Title']}-{song['Artist']}"
            if song_key not in listbox_items:
               self.Queue_listbox.insert(tkinter.END,song_key)
               

    def buttonListbox(self):
     # made the buttons show up 
     self.btnAddToListbox =  tkinter.Button(self.frames["down"], text = "Add",bg="SystemButtonFace", activebackground="Black", fg="Black", command = self.addSong).grid(row=2, column=4)
     self.btnDeleteToListbox =  tkinter.Button(self.frames["down"], text = "Delete",bg="SystemButtonFace", activebackground="Black", fg="Black", command = self.deleteSong).grid(row=3, column=4)
     self.btnUpToListbox = tkinter.Button(self.frames["down"], text = "↑",bg="SystemButtonFace", activebackground="Black", fg="Black",command = self.upListbox).grid(row=2, column=2, sticky="nes")
     self.btnDownToListbox = tkinter.Button(self.frames["down"], text = "↓",bg="SystemButtonFace", activebackground="Black", fg="Black",command = self.downListBox).grid(row=3, column=2, sticky="nes")
     self.grid_columnconfigure(0,weight=1)
     self.grid_rowconfigure(1,weight=0)
     self.grid_rowconfigure(2,weight=1)
     #Click  
    # def myClick(self):
    #     self.btnAddToListbox = tkinter.Label(self.frames["down"], text = "Add",bg="SystemButtonFace", activebackground="Black", fg="Black").grid(row=1, column=5)
    # def myRelease(self):
    def addSong(self):
        #this function needs some work
        # put the selected song into the queue
        file_path = filedialog.askopenfilename()

        #need to change file_path to be ID
        #file Selector
        #FileName Change
        self.queueSong(file_path)
        i = file_path

        print(file_path)
        if i.lower().endswith(".mp3"):
            mp3 = eyed3.load(file_path)

            if mp3:
                trackTitle = mp3.tag.title
                trackArtist = mp3.tag.artist
                trackAlbum = mp3.tag.album
                trackRD = mp3.tag.getBestDate()
                trackImage = False
            else:
                print("Error loading MP3")

            # if trackTitle == None: trackTitle = "Unknown"
            # if trackArtist == None: trackArtist = "Unknown"
            # if trackAlbum == None: trackAlbum = "Unknown"
            # if trackRD == None: trackRD = "Unknown"

            #this generates the imgs from the mp3s
            if mp3.tag.images:
                for image in mp3.tag.images:
                    image_file = open(f"..\\imgs\\{self.idCounter} - {trackTitle} - {trackArtist}().jpg","wb+")
                    image_file.write(image.image_data)
                    image_file.close()
                    trackImage = True
            else:
                self.canvasAlbum.delete("all")
                self.canvasAlbum.grid_remove()
                self.canvasAlbum.grid(row=1,column=1)
                # self.canvasAlbum.pack(side = "left", fill = "both", expand = True ,padx=2,pady=2)
                self.genAlbumIcon(2)
                trackImage = False
    
            #This append function prevents the program from loading mp3 files that have no image, because each ID in the array must include a value for trackImage
        self.songs.append({"id":self.idCounter,"Title":trackTitle,"Artist":trackArtist,"Album":trackAlbum,"Release":trackRD,"Image":trackImage,"Directory":i,"Length":mp3.info.time_secs})
            # print(mp3.info.time_secs, end = " | ")
        self.idCounter += 1
        #Get the last added song's index (assumming 0-based indexing)
        new_song_index = len(self.songs)-1
        # never reaches the bottom of list
        # adding new song index makes it pop right away but looks like icon of first
        # if you click add and next then no error
        song_key = f"{self.songs[new_song_index]['id']}: {self.songs[new_song_index]['Title']}-{self.songs[new_song_index]['Artist']}"
        self.Queue_listbox.insert(tkinter.END,song_key)
       # self.refresh()
        
      #  if song_key not in self.Queue_listbox.gen(0,tkinter.END):
      #      self.Queue_listbox.insert(tkinter.END,song_key)
       # self.loadIntoListbox()
        # load into listbox doesn't show new song just when next or previous is pressed
        # ONLY HITING NEXT BUTTON SHOWS ADDED SONG

    def deleteSong(self):
        current = self.Queue_listbox.curselection() 
        current = int(current[0])# convert to int

        if 0 <= current <= self.Queue_listbox.size():
            item_text = self.Queue_listbox.get(current)
            self.Queue_listbox.delete(current)

        targetId = item_text[0].split(":",1)[0]
        
        for song in self.songs:
         
            if str(song["id"]) == targetId:
                self.songs.remove(song)
                print(self.songs)


    

    def upListbox(self):
        current = self.Queue_listbox.curselection() 

        if not current:#check if there is a selection
            return

        current = int(current[0])# convert to int

        if current == 0: # check to see if song already at top
            return 
        if 0 < current <= self.Queue_listbox.size():
            item_text = self.Queue_listbox.get(current)
            self.Queue_listbox.delete(current)
        insert_index = current - 1 

        if insert_index < 0:# position 1 is the first songs
            insert_index = 0

        self.Queue_listbox.insert(insert_index,item_text)
       
        #take text we have split it whereever we see a collun
        # take the first half of it
        targetId = item_text[0].split(":",1)[0]
        
        for song in self.songs:
         
            if str(song["id"]) == targetId:
                self.songs.remove(song)
                self.songs.insert(insert_index,song)


        #Change song order cuases errors
        #self.changeSongOrder()
   # print ("Popped Element",self.songQueued.pop()), Doesn't like this wants a input


    def downListBox(self):
        current = self.Queue_listbox.curselection() 

        if not current:#check if there is a selection
            return

        current = int(current[0])# convert to int

        if 0 <= current <= self.Queue_listbox.size():
            item_text = self.Queue_listbox.get(current)
            self.Queue_listbox.delete(current)
        insert_index = current + 1 

        if insert_index == self.Queue_listbox.size() -1: # position 1 is the first songs
            insert_index = self.Queue_listbox.size() -1

        self.Queue_listbox.insert(insert_index,item_text)
       
        #take text we have split it whereever we see a collun
        # take the first half of it
        targetId = item_text[0].split(":",1)[0]
        
        for song in self.songs:
         
            if str(song["id"]) == targetId:
                self.songs.remove(song)
                self.songs.insert(insert_index,song)




    def ListboxRemoveOldSongs(self):
        for song in self.songs:
            self.Queue_listbox.delete(1)

    def ListboxHighlightPlaying(self):
        currentSong = self.songQueued
        print("THE CURRENT SONG",currentSong) 
        for index, song in enumerate(self.songs):
            if song["id"]== currentSong["id"]:
                break
        self.Queue_listbox.selection_clear(0,tkinter.END)
        self.Queue_listbox.selection_set(index)
        

"""
    def ListboxNextEvent(self):
        global index_of_song
        index_of_song = 1
        if self.Queue_listbox.size() == index_of_song:
            index_of_song = 0
        self.Queue_listbox.selection_clear(0,tkinter.END)
        self.Queue_listbox.selection_set(index_of_song)
     


    def ListboxPrevEvent(self):
        global index_of_song 
        index_of_song = index_of_song - 1
        if  index_of_song == 0:
            index_of_song = self.Queue_listbox.size() - 1
            self.Queue_listbox.selection_clear(0,tkinter.END)
            self.Queue_listbox.selection_set(index_of_song)   
        self.Queue_listbox.selection_clear(0,tkinter.END)
        self.Queue_listbox.selection_set(index_of_song) 

    def ListboxDirectoryEvent(self):
        global index_of_song 
        index_of_song = 0
        self.Queue_listbox.selection_clear(0,tkinter.END)
        self.Queue_listbox.selection_set(index_of_song) 

    # just made today.
    def changeSongOrder(self):
        if len(self.songs)>=3:
            self.songs[1],self.songs[0] = self.songs[0],self.songs[1]
            self.queueSong(1)
        else:
            print("Not enought songs to change the order")
    """

# this runs the whole file
Window().mainloop()