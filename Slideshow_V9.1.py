from tkinter import *
from PIL import ImageTk, Image
import os

# Set up the tkinter window
root = Tk()
root.title("Image Slideshow")
root.geometry("800x800")

# Load images from the "computed_game" subdirectory
image_list = []
subdirectory = "computed_game"

# Check if the subdirectory exists
if os.path.exists(subdirectory):
    for file in os.listdir(subdirectory):
        if file.endswith(('png', 'jpg', 'jpeg', 'gif')):
            img_path = os.path.join(subdirectory, file)
            img = ImageTk.PhotoImage(Image.open(img_path).resize((800, 800)))
            image_list.append(img)
else:
    print(f"The directory '{subdirectory}' does not exist.")

counter = 0
is_toggling = False
toggle_interval = 250  # milliseconds

def show_image():
    if image_list:  # Check if there are images to display
        imageLabel.config(image=image_list[counter])


def next_image():
    global counter
    counter = (counter + 1) % len(image_list)
    show_image()

def previous_image():
    global counter
    counter = (counter - 1) % len(image_list)
    show_image()

def reset_slideshow():
    global counter
    counter = 0
    show_image()

def toggle_images():
    global is_toggling, previous_counter

    if is_toggling:
        is_toggling = False
        toggle_button.config(text="Start Comparing")
        return_to_manual_mode()
    else:
        is_toggling = True
        toggle_button.config(text="Stop Comparing")
        previous_counter = (counter - 1) % len(image_list)  # Store previous image index
        alternate_images()

def alternate_images():
    global counter, previous_counter

    if is_toggling:
        # Alternate between current and previous image
        current_image = image_list[counter]
        previous_image = image_list[previous_counter]

        # Show current image first, then switch to previous image
        if imageLabel.cget('image') == str(current_image):
            imageLabel.config(image=previous_image)
        else:
            imageLabel.config(image=current_image)

        # Schedule the next toggle after the specified interval
        root.after(toggle_interval, alternate_images)

def return_to_manual_mode():
    show_image()  # Show the current image when toggled off

# Set up the components
imageLabel = Label(root)
infoLabel = Label(root, font="Helvetica, 20")

nextButton = Button(root, text="Next", command=next_image)
prevButton = Button(root, text="Previous", command=previous_image)
resetButton = Button(root, text="Reset", command=reset_slideshow)
toggle_button = Button(root, text="Start Comparing", command=toggle_images)

# Display the components
imageLabel.pack()
infoLabel.pack()
prevButton.pack(side="left")
nextButton.pack(side="right")
resetButton.pack(side="top")
toggle_button.pack(side="bottom")

# Run the main loop
show_image()
root.mainloop()
