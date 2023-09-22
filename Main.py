from pygame import mixer

def playSong(directory):
    mixer.init()
    mixer.music.load(directory)
    mixer.music.play()

#mixer.music.pause() - this is how to pause the music
#mixer.music.unpause() - this is how to unpause the music
from tkinter import *
from PIL import Image, ImageTk

def configure_frames():
    window.grid_rowconfigure(0, weight=1)  # Allow the top row (containing left and right frames) to expand vertically
    window.grid_columnconfigure(0, weight=1)  # Allow the first column (containing left frame) to expand horizontally
    window.grid_columnconfigure(1, weight=1)  # Allow the second column (containing right frame) to expand horizontally
    window.grid_rowconfigure(1, weight=1)  # Allow the bottom row (containing down frame) to expand vertically
    
    


def resize_image(event):
    # Calculate the new dimensions while maintaining the aspect ratio
    original_width, original_height = img_1.size
    window_width = event.width - 20  # Adjust for padding
    window_height = event.height - 50  # Adjust for padding

    # Calculate the scaling factor for both width and height
    width_scale = window_width / original_width
    height_scale = window_height / original_height

    # Use the smaller scaling factor to maintain the aspect ratio
    min_scale = min(width_scale, height_scale)

    # Resize the image with the calculated scaling factor
    new_width = int(original_width * min_scale)
    new_height = int(original_height * min_scale)
    resized_image = img_1.resize((new_width, new_height), Image.ANTIALIAS)

    # Update the label with the resized image
    new_photo = ImageTk.PhotoImage(resized_image)
    app_image.configure(image=new_photo)
    app_image.image = new_photo
    

def resize_elements(event):   
    # Resize and update the play button image
    original_width, original_height = img_2.size
    window_width = event.width - 20  # Adjust for padding
    window_height = event.height - 50
    resized_play_img = img_2.resize((new_width, new_height), Image.ANTIALIAS)
    new_play_img = ImageTk.PhotoImage(resized_play_img)
    play_button.configure(image=new_play_img)
    play_button.image = new_play_img
    
    # Resize and update the prev button image
    resized_prev_img = img_3.resize((new_width, new_height), Image.ANTIALIAS)
    new_prev_img = ImageTk.PhotoImage(resized_prev_img)
    prev_button.configure(image=new_prev_img)
    prev_button.image = new_prev_img
    
    # Resize and update the next button image
    resized_next_img = img_4.resize((new_width, new_height), Image.ANTIALIAS)
    new_next_img = ImageTk.PhotoImage(resized_next_img)
    next_button.configure(image=new_next_img)
    next_button.image = new_next_img
    
    # Resize and update the pause button image
    resized_pause_img = img_5.resize((new_width, new_height), Image.ANTIALIAS)
    new_pause_img = ImageTk.PhotoImage(resized_pause_img)
    pause_button.configure(image=new_pause_img)
    pause_button.image = new_pause_img
    
    # Resize and update the continue button image
    resized_continue_img = img_6.resize((new_width, new_height), Image.ANTIALIAS)
    new_continue_img = ImageTk.PhotoImage(resized_continue_img)
    continue_button.configure(image=new_continue_img)
    continue_button.image = new_continue_img
    
    # Resize and update the stop button image
    resized_stop_img = img_7.resize((new_width, new_height), Image.ANTIALIAS)
    new_stop_img = ImageTk.PhotoImage(resized_stop_img)
    stop_button.configure(image=new_stop_img)
    stop_button.image = new_stop_img
    


co1 = 'white'
co2 = "#3C1DC6"
co3 = "#333333"
co4 = "#CFC7F8"

window = Tk()
window.title("")
window.geometry('325x225')
window.configure(background=co1)
window.resizable(width=True, height=True)
window.state('zoomed')

# frames
left_frame = Frame(window, width=150, height=150, bg=co1)
left_frame.grid(row=0, column=0, padx=1, pady=1, sticky="nsew")
right_frame = Frame(window, width=250, height=150, bg=co3)
right_frame.grid(row=0, column=1, padx=0, sticky="nsew")
down_frame = Frame(window, width=400, height=100, bg=co4)
down_frame.grid(row=1, column=0, columnspan=3, padx=0, pady=1, sticky="nsew")

# Open the image
img_1 = Image.open("C:/Users/rajya/OneDrive - SNHU/MP3 PROJECT CS250/mp3.png")
# Create a label to display the image
app_image = Label(left_frame)
app_image.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

#opening buttons
img_2 = Image.open("C:/Users/rajya/OneDrive - SNHU/MP3 PROJECT CS250/play.png")

play_button = Button(down_frame, image=img_2, padx=10, bg=co1)
play_button.grid(row=0, column=0, padx=10,  sticky="nsew")


# Call the configure_frames function to make the frames resizable
configure_frames()

# Bind the resize_image function to the <Configure> event of the window
window.bind("<Configure>", resize_image)

window.mainloop()
