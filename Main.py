from pygame import mixer

def playSong(directory):
    mixer.init()
    mixer.music.load(directory)
    mixer.music.play()

#mixer.music.pause() - this is how to pause the music
#mixer.music.unpause() - this is how to unpause the music