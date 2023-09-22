import eyed3

mp3 = eyed3.load('Directory')

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