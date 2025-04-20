from tkinter import *
from tkinter.ttk import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfilename, asksaveasfilename
from PIL import Image, ImageTk, ImageDraw, ImageFont
from fonts import FONTS
import os

basedir = os.path.dirname(__file__)


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def width_slider_moved(event):
    width_label.configure(text=f"Width: {current_width.get() - 1/2 * img_width}")


def height_slider_moved(event):
    height_label.configure(text=f"Height: {-1 * (current_height.get()  - 1/2 * img_height)}")


def enter_pressed(event):
    apply_watermark()


def change_text_color():
    colors = askcolor(title="Watermark Color Chooser")
    global text_color
    text_color = colors[0]
    color_selection.configure(bg=colors[1])


def apply_watermark():
    watermark_image = image.convert('RGBA')
    my_font = ImageFont.truetype(font_var.get(), current_font_size.get())

    # Blank image for text
    blank_image_dims = (round(4 * watermark_image.width),
                        round(4 * watermark_image.height))
    text_image = Image.new('RGBA', blank_image_dims, (255, 255, 255, 0))
    my_watermark = ImageDraw.Draw(text_image)

    # Create RGBA tuple from color choice and opacity value
    opacity_tuple = ((round(current_opacity.get() * 2.55)),)
    rgba_text_color = text_color + opacity_tuple

    # Setup Watermark
    center_of_image = (round(text_image.width / 2), round(text_image.height / 2))
    my_watermark.text(center_of_image,
                      watermark_input.get(),
                      font=my_font,
                      fill=rgba_text_color,
                      anchor="mm",)

    text_box_size = text_image.getbbox()
    text_image = text_image.crop(text_box_size)
    text_image = text_image.rotate(current_tilt.get(),
                                   center=(text_image.width / 2, text_image.height / 2),
                                   expand=True)

    d = Image.new('RGBA', watermark_image.size, (255, 255, 255, 0))
    text_position = ((int(current_width.get() - text_image.width / 2),
                      int(current_height.get() - text_image.height / 2)))
    Image.Image.paste(d, text_image, text_position)

    combined = Image.alpha_composite(watermark_image, d).convert('RGB')
    combined.save((os.path.join(basedir, "new_img_with_watermark.jpeg")), format='JPEG')  # To concat current directory
    watermark_image.close()

    updated_image = ImageTk.PhotoImage(Image.open(os.path.join(basedir, "new_img_with_watermark.jpeg")))
    label.configure(image=updated_image)
    label.image = updated_image


def file_open():
    global image, img_width, img_height
    image_path = askopenfilename(title="Select An Image", filetypes=[('Images', '*.jpg *.jpeg *.png *.webp *.gif')])
    if image_path:
        img_width, img_height = Image.open(image_path).size

        width_position.config(to=img_width)
        height_position.config(to=img_height)
        width_label.configure(text="Width: ")
        height_label.configure(text="Height: ")
        current_width.set(int(img_width / 2))
        current_height.set(int(img_height / 2))

        image = Image.open(image_path)
        img_width = int(img_width*(750/img_height))
        image = image.resize((img_width, 750))

        uploaded_image = ImageTk.PhotoImage(image)
        label.configure(image=uploaded_image)
        label.image = uploaded_image
        apply_watermark()
    else:
        remove_files()
        quit()


def remove_files():
    os.remove("blank_image.jpeg")  # To remove file
    if os.path.exists("new_img_with_watermark.jpeg"):  # To check whether a particular path exists
        os.remove("new_img_with_watermark.jpeg")
    if os.path.exists("temp_image.jpeg"):
        os.remove("temp_image.jpeg")


def another_watermark():
    global image
    temp_image = Image.open(os.path.join(basedir, "new_img_with_watermark.jpeg"))
    temp_image.save(os.path.join(basedir, "temp_image.jpeg"))
    image = (os.path.join(basedir, "temp_image.jpeg"))
    temp_image.close()


def save_new_image():
    new_image = Image.open(os.path.join(basedir, "new_img_with_watermark.jpeg"))
    file = asksaveasfilename(title="Save Image", filetypes=[("jpeg files", "*.jpg")])
    if file:
        new_image.save(file)
    new_image.close()


window = Tk()
window.title("Image Watermark")
window.resizable(False, False)

image_frame = Frame(window)
image_frame.pack(side=LEFT, padx=10, pady=10)

blank_image = Image.new('RGB', (600, 600), color='white')
blank_image.save((os.path.join(basedir, "blank_image.jpeg")))
image = (os.path.join(basedir, "blank_image.jpeg"))
img = ImageTk.PhotoImage(Image.open(image))
label = Label(image_frame, image=img)
label.grid(column=0, row=0)


edit_frame = Frame(window, height=600)
edit_frame.pack(padx=10, pady=10)

upload_button = Button(edit_frame,
                       text="Upload Image",
                       command=file_open,
                       style="Wide.TButton")
upload_button.grid(column=0, row=0, columnspan=2)

watermark_label = Label(edit_frame, text="Watermark Text: ", anchor="w")
watermark_label.grid(column=0, row=1)
watermark_input = Entry(edit_frame, width=22)
watermark_input.grid(column=1, row=1)

font_label = Label(edit_frame, text="Font: ", width=12, anchor="w")
font_label.grid(column=0, row=2)
font_var = StringVar()
drop_menu = OptionMenu(edit_frame, font_var, FONTS[0], *FONTS)
drop_menu.grid(column=1, row=2)

current_font_size = IntVar(value=30)
font_size_label = Label(edit_frame, text="Font size: ", width=12, anchor="w")
font_size_label.grid(column=0, row=3)
font_size = Spinbox(edit_frame,
                    from_=8,
                    to=250,
                    wrap=True,
                    textvariable=current_font_size,)
font_size.grid(column=1, row=3)

current_opacity = IntVar(value=100)
opacity_label = Label(edit_frame, text="Opacity", width=12, anchor="w")
opacity_label.grid(column=0, row=4)
opacity_spinbox = Spinbox(edit_frame,
                          from_=0,
                          to=100,
                          textvariable=current_opacity,
                          wrap=False,
                          )
opacity_spinbox.grid(column=1, row=4)

text_color = (0, 0, 0)
color_selection = Canvas(edit_frame,
                         bg=rgb_to_hex(text_color),
                         width=110,
                         height=15)
color_selection.grid(column=0, row=5)
color_button = Button(edit_frame,
                      text="Change Color",
                      command=change_text_color,
                      style="Color.TButton",
                      width=18)
color_button.grid(column=1, row=5, columnspan=1)

img_width, img_height = 600, 600
height_label = Label(edit_frame, text="Height: ", width=12, anchor="w")
height_label.grid(column=0, row=6)
current_height = IntVar(value=int(img_height / 2))
height_position = Scale(edit_frame,
                        from_=0,
                        to=img_height,
                        variable=current_height,
                        orient=VERTICAL,
                        command=height_slider_moved)
height_position.grid(column=1, row=6)

width_label = Label(edit_frame, text="Width: ", width=12, anchor="w")
width_label.grid(column=0, row=7)
current_width = IntVar(value=int(img_height / 2))
width_position = Scale(edit_frame,
                       from_=0,
                       to=img_width,
                       variable=current_width,
                       orient=HORIZONTAL,
                       command=width_slider_moved)
width_position.grid(column=1, row=7)

current_tilt = IntVar(value=0)
tilt_label = Label(edit_frame, text="Tilt: ", width=12, anchor="w")
tilt_label.grid(column=0, row=8)
tilt_spinbox = Spinbox(edit_frame,
                       from_=0,
                       to=359,
                       wrap=True,
                       textvariable=current_tilt,
                       )
tilt_spinbox.grid(column=1, row=8)
# Apply/Update Button
confirm_button = Button(edit_frame,
                        text="Update Watermark",
                        command=apply_watermark,
                        style="Wide.TButton")
confirm_button.grid(column=0, row=9, columnspan=2)

another_wm_button = Button(edit_frame,
                           text="Apply Another Watermark",
                           command=another_watermark,
                           style="Wide.TButton")
another_wm_button.grid(column=0, row=10, columnspan=2)

save_button = Button(edit_frame,
                     text="Save",
                     command=save_new_image,
                     style="Wide.TButton")
save_button.grid(column=0, row=11, columnspan=2)


window.bind('<Return>', enter_pressed)


style = Style(window)
style.configure('Wide.TButton', width=30, padding=5)


window.withdraw()
file_open()
window.deiconify()

if __name__ == '__main__':
    window.mainloop()
    remove_files()