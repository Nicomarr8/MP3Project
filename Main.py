from pygame import mixer

def playSong(directory):
    mixer.init()
    mixer.music.load(directory)
    mixer.music.play()