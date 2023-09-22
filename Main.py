import eyed3
from pygame import mixer

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

#mixer.music.pause() - this is how to pause the music
#mixer.music.unpause() - this is how to unpause the music
