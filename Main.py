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

        self.createListbox()
       
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

        # Allows the user to select a directory and automatically update the list in the application
        def select_directory():
            self.directory = filedialog.askdirectory() 
            self.removeButtons()          
            self.refresh() 
            self.loadSongs()
            self.songScrollbar.update()

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
            self.seek.config(label="00:00")
            #loads and then plays the selected song
            self.mixer.music.load(self.directory + "\\" + self.songQueued["Directory"])
            self.mixer.music.play()
            #Loads into listbox
            self.loadIntoListbox()
            if self.paused: self.pause()
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
            self.Queue_listbox.delete(1)
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
            #sizeOfmyListbox = self.Queue_listbox.size(self)
            #for x in range(sizeOfmyListbox):
            #    self.Queue_listbox.delete(x)
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
        if -1 < self.songQueued["id"] + direction < len(self.songs):
            self.queueSong(self.songs[self.songQueued["id"] + direction]["id"])
        elif self.songQueued["id"] + direction <= -1:
            self.queueSong(self.songs[len(self.songs)-1]["id"])
        elif self.songQueued["id"] + direction > len(self.songs)-1:
            self.queueSong(self.songs[0]["id"])
            



    def moveSeek(self,event):
        self.seek.config(label=f"{int(self.seek.get() / 60):02d}:{int((float(self.seek.get() / 60) - int(self.seek.get() / 60)) * 60 ):02d}")
        if self.seek.get() == int(self.songQueued["Length"]) and not self.paused:
            self.Queue_listbox.delete(1)
            self.moveSong(1)
            

       #Favorites
            self.favorites=[]
            self.load_favorites()
            self.load_songs()
            self.refresh ()

           

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

    def createListbox(self):# got rid of factor
            self.listbox_scrollbar = tkinter.Scrollbar(self.frames["down"],orient = "vertical")
            self.Queue_listbox = tkinter.Listbox(self.frames["down"], bg = "white", yscrollcommand=self.listbox_scrollbar.set)   
            self.Queue_listbox.insert(tkinter.END, "SongQueue")
            self.Queue_listbox.config(yscrollcommand=self.listbox_scrollbar.set)        
            self.listbox_scrollbar.config(command=self.Queue_listbox.yview)
            self.Queue_listbox.grid(row=1, column =3,sticky ="nsew" ) 
            self.listbox_scrollbar.grid(row=1, column=4,sticky="nsw")   
    def loadIntoListbox(self):# got rid of factor
        #Add songs to the listbox.
        listbox_items = self.Queue_listbox.get(0,tkinter.END)
        for song in self.songs:
            song_key = f"{song['Title']}-{song['Artist']}"
            if song_key not in listbox_items:
               self.Queue_listbox.insert(tkinter.END,song_key)
   # def ListboxEvents(self):#factor
       # if move

   
    
    # Create a listbox to display the song queue
"""   def createListbox(self,factor):
        self.Queue_listbox = tkinter.Listbox(self.frames["down"], bg="white")
        self.Queue_listbox.grid(row=1, column=3, sticky="nsew")
        self.Queue_listbox.bind("<Delete>", self.delete_selected_song)
        self.Queue_listbox.bind("<Up>", self.move_up)
        self.Queue_listbox.bind("<Down>", self.move_down)

# A function to add a song to the queue
def add_song_to_queue(self, song_id):
    song = self.get_song_by_id(song_id)
    if song:
        self.song_queue.append(song)
        self.Queue_listbox.insert(tkinter.END, f"{song['Title']} - {song['Artist']}")

# A function to remove a song from the queue
def remove_song_from_queue(self, song_id):
    song = self.get_song_by_id(song_id)
    if song in self.song_queue:
        index = self.song_queue.index(song)
        self.song_queue.remove(song)
        self.Queue_listbox.delete(index)

# A function to delete the selected song from the queue
def delete_selected_song(self):
        # Get the currently selected index in the listbox
        selected_index = self.Queue_listbox.curselection()

        if selected_index:
            index_to_delete = int(selected_index[0])

            # Remove the item from the listbox
            self.Queue_listbox.delete(index_to_delete)

            # Also, remove the corresponding item from your internal song list (assuming you have a list of songs)
            if 0 <= index_to_delete < len(self.songs):
                del self.songs[index_to_delete]

# A function to move the selected song up in the queue
def move_up(self, event):
    selected_index = self.Queue_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        if index > 0:
            self.swap_songs_in_queue(index, index - 1)

# A function to move the selected song down in the queue
def move_down(self, event):
    selected_index = self.Queue_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        if index < len(self.song_queue) - 1:
            self.swap_songs_in_queue(index, index + 1)

# A function to swap two songs in the queue
def swap_songs_in_queue(self, index1, index2):
    song1 = self.song_queue[index1]
    song2 = self.song_queue[index2]
    self.song_queue[index1] = song2
    self.song_queue[index2] = song1
    self.update_queue_listbox()

# A function to update the listbox with the current queue
def update_queue_listbox(self):
    self.Queue_listbox.delete(0, tkinter.END)
    for song in self.song_queue:
        self.Queue_listbox.insert(tkinter.END, f"{song['Title']} - {song['Artist']}")

# A function to get a song by its ID
def get_song_by_id(self, song_id):
    for song in self.songs:
        if song["id"] == song_id:
            return song
    return None
"""



                
    

"""
    selected_index = self.Queue_listbox.curselection()
        if selected_index:
            new_index = int(selected_index[0]) + 1  # Insert after the selected item

             # Insert your new item at the desired position (new_index)
            self.Queue_listbox.insert(new_index, "Your New Song Title")

            # Optionally, update your internal song list to match the listbox
            self.songs.insert(new_index, {"Title": "Your New Song Title", "Artist": "Artist Name"})

            # You can also clear the previous selection
            self.Queue_listbox.selection_clear(selected_index)
            

def delete_selected_song(self):
    # Get the currently selected index in the listbox
    selected_index = self.Queue_listbox.curselection()

    if selected_index:
        index_to_delete = int(selected_index[0])
        
        # Remove the item from the listbox
        self.Queue_listbox.delete(index_to_delete)
        
        # Also, remove the corresponding item from your internal song list
        del self.songs[index_to_delete]


    def move_up(self, event):
        selected_index = self.Queue_listbox.curselection()
        if selected_index:
            new_index = int(selected_index[0]) - 1
            if new_index >= 0:
                self.Queue_listbox.selection_clear(selected_index)
                self.Queue_listbox.selection_set(new_index)
                self.Queue_listbox.see(new_index)

    def move_down(self, event):
         selected_index = self.Queue_listbox.curselection()
         if selected_index:
            new_index = int(selected_index[0]) + 1
            if new_index < self.Queue_listbox.size():
                self.Queue_listbox.selection_clear(selected_index)
                self.Queue_listbox.selection_set(new_index)
                self.Queue_listbox.see(new_index)
"""
# this runs the whole file
Window().mainloop()