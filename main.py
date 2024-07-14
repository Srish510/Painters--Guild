from tkinter import *
from tkinter import filedialog
from tkinter import font
import customtkinter
from CTkColorPicker import *
from GF import GradientFrame
from PIL import Image, ImageTk
import PIL.ImageGrab as ImageGrab
from tkinter import messagebox

#Root Declaration:
root = customtkinter.CTk() 
root.geometry("1400x780")
root.title("Painters' Guild")
root.after(201, lambda :root.iconbitmap('icon.ico'))

#Variables:
state = "draw"
prevColor = "black"
erased = False
prevPoint = [0,0]
currPoint = [0,0]
lineWidth = 1
drawColor = "black"
backColor = "white"  
eraseCursor = ImageTk.PhotoImage(Image.open("erase_cursor.png"))
start_x, start_y = 0, 0
shape_id = None
textTick = False
textFont = 'Arial'
style = ''
textSize = 12
available_fonts = list(font.families())
textFrame = None
selection_rectangle = None
selection_start = None
selection_end = None
selected_image = None
penciled = True
pencilMark = []
drawMark = []
undo_stack = []
redo_stack = []

#---Util Frame:

util = Frame(root , height=55 , width=1750 , bg="gray92")
util.grid(row=0 , column=0)

#Save Button:
def saveImage():
    try:
        Loc = filedialog.asksaveasfilename(defaultextension="jpg")
        x = canvas.winfo_rootx()
        y = canvas.winfo_rooty()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, x1 - 2, y1 - 2))
        img.save(Loc)
        showImage = messagebox.askyesno("Painters' Guild", "Do you want to open the saved image?")
        if showImage:
            img.show()
    except Exception as e:
        messagebox.showinfo("Painters' Guild", "Something went wrong!")

save = customtkinter.CTkButton(util, text="Save", width = 20, text_color = "white", command = saveImage)     
save.place(x=10, y=23, anchor=W)

#Clear Button:
def clear_canv():
    clearCanv = messagebox.askyesno("Painters' Guild", "Do you want to clear the canvas?")
    if clearCanv:
        canvas.delete("all")

clear = customtkinter.CTkButton(util, text="Clear", width = 20, text_color = "white", command = clear_canv)
clear.place(x=60, y=23, anchor=W)

#Background Button:
def ask_back_color():
    global backColor, drawColor
    pick_color = AskColor() # open the color picker
    color = pick_color.get() # get the color string
    backColor = color
    canvas.configure(bg = backColor)
    if isToggled(eraser):
        drawColor = color

background = customtkinter.CTkButton(util, text="Background", width = 20, text_color = "white", command = ask_back_color)
background.place(x=110, y=23, anchor=W)

#Clear Pencil Button:
def clear_pencil():

    clearPen = messagebox.askyesno("Painters' Guild", "Do you want to clear all pencil strokes? This action can't be undone!")
    if clearPen:
        for item in pencilMark:
            canvas.delete(item)

clearPencil = customtkinter.CTkButton(util, text="Clear Pencil", width = 20, text_color = "white", command = clear_pencil)
clearPencil.place(x = 200, y=23, anchor=W)

def perform_undo():
    if undo_stack:
        action = undo_stack.pop()
        redo_stack.append(action)
        if action[0] == "draw":
            for i in action[1]:
                canvas.delete(i[0])
        elif action[0] in shapes:
            canvas.delete(action[1])
        elif action[0] == "text":
            canvas.delete(action[1])
        elif action[0] == "image":
            canvas.delete(action[1])

def perform_redo():
    global oldVal
    if redo_stack:
        action = redo_stack.pop()
        undo_stack.append(action)
        if action[0] == "draw":
            for i in action[1]:
                canvas.create_polygon(i[1], fill=action[2], outline=action[2], width=action[3])
        elif action[0] in shapes:        
            shape_id = draw_shape(action[0], action[2],action[3],action[4])
            canvas.configure(height= action[5], width = action[6])
            action = (action[0], shape_id, action[2],action[3],action[4])
        elif action[0] == "text":
            canvas.create_text(action[2], text=action[3], fill=action[4], font=action[5])
            canvas.configure(height= action[6], width = action[7])
        elif action[0] == "image":
            canvas.create_image(action[2], anchor=NW, image=action[3])
            canvas.configure(height= action[4], width = action[5])

#Undo Button:
undo_image = customtkinter.CTkImage(Image.open("undo.png"), size = (30,30))
undo = customtkinter.CTkButton(util, fg_color = "transparent", text = "", image = undo_image, width = 5, hover_color = "white", command= perform_undo)
undo.place(x = 287, y=23, anchor=W)

#Redo Button:
redo_image = customtkinter.CTkImage(Image.open("redo.png"), size = (30,30))
redo = customtkinter.CTkButton(util, fg_color = "transparent", text = "", image = redo_image, width = 5, hover_color = "white", command=perform_redo)
redo.place(x = 337, y=23, anchor=W)

#----------------------------------------------------------------------------------------------------------------------------------

#---Canvas: 

#Canvas Frame:
canv_frame = GradientFrame(root, colors = ("gray63", "gray92"), height=778 , width=1753)
canv_frame.config(direction = canv_frame.top2bottom)
canv_frame.place(x = -3, y = 195)

#The Actual Canvas:
canv_height, canv_width = 600, 1280
changed_height = canv_height
changed_width = canv_width
canvas = Canvas(canv_frame, height = canv_height , width = canv_width, bg = backColor)
canvas.place(relx=0.5, rely=0.5, anchor=CENTER)

#Screen Slider: (Future Update)
'''
oldVal = 1.0

def sliding(value):
    global oldVal
    global changed_height, changed_width
    val = float(value) / 100  
    slid.configure(text=f"{int(value)}")
    scale_factor = val / oldVal
    canvas.scale("all", 0, 0, scale_factor, scale_factor)
    changed_width = int(canv_width * val)
    changed_height = int(canv_height * val)
    canvas.config(width = changed_width, height = changed_height)
    oldVal = val

slid = customtkinter.CTkLabel(canv_frame, text = "100", font = ("Helvetica", 13), text_color = "black", fg_color= "transparent")
slid.place(x=1375,y=604,anchor = SE)

slider = customtkinter.CTkSlider(canv_frame, 
                                 from_ = 50,
                                 to = 120,
                                 command = sliding,
                                 fg_color= "PaleGreen2",
                                 progress_color="SpringGreen3",
                                 button_color = "forest green",
                                 button_hover_color = "SeaGreen1")
slider.set(100)
slider.place(x=1380,y=615,anchor = SE)
'''

#---------------------------------------------------------------------------------------------------------------------------------

#---Tools Frame:

tools = Frame(root , height=140 , width=1750 , bg="gray87")
tools.place(x = 0, y = 55)

#Kit:

kit = Frame(tools, height = 140, width = 250, bg = "gray87")
kit.place(x = 470, y = 5)

def toggle(button):
    global penciled
    button.configure(fg_color = "white", border_color = "CadetBlue3", border_width = 1)
    for item in kit.winfo_children():
        if item != button:
            untoggle(item)
    if button == pencil:
        penciled = True
    else:
        penciled = False

def untoggle(button):
    button.configure(fg_color = "gray87", border_color = "gray87")
    if button == text and textFrame:
        textFrame.destroy()

def isToggled(button):
    if (button.cget("fg_color") == "white") and (button.cget("border_color") == "CadetBlue3"):
        return True
    else:
        return False

#Pencil:
def usePencil():
        global prevColor
        global drawColor
        global erased
        global state
        state = "draw"
        if isToggled(pencil):
            untoggle(pencil)
            state = ""
        else:
            toggle(pencil)
            if erased == True:
                drawColor = prevColor
        erased = False        

pencil_image = customtkinter.CTkImage(Image.open("pencil.png"), size = (27,27))
pencil = customtkinter.CTkButton(kit, fg_color = "transparent", text = "", image = pencil_image, width = 5, hover_color = "white", command = usePencil)
pencil.place(x = 5, y = 5)
toggle(pencil)

#Brush:
def useBrush():
        global prevColor
        global drawColor
        global erased
        global state
        global penciled
        state = "draw"
        if isToggled(brush):
            untoggle(brush)
            toggle(pencil)
        else:
            toggle(brush)
            if erased == True:
                drawColor = prevColor
        erased = False

brush_image = customtkinter.CTkImage(Image.open("brush.png"), size = (27,27))
brush = customtkinter.CTkButton(kit, fg_color = "transparent", text = "", image = brush_image, width = 5, hover_color = "white", command = useBrush)
brush.place(x = 60, y = 5)

#Eraser:
def useEraser():
        global drawColor
        global prevColor
        global erased
        global state
        global penciled
        state = "draw"
        eraser['state'] = NORMAL
        if isToggled(eraser):
            untoggle(eraser)
            drawColor = prevColor
            toggle(pencil)
            erased = False
            penciled = True
        else:
            toggle(eraser)
            prevColor = drawColor
            drawColor = backColor
            erased = True

eraser_image = customtkinter.CTkImage(Image.open("eraser.png"), size = (32,32))
eraser = customtkinter.CTkButton(kit, fg_color = "transparent", text = "", image = eraser_image, width = 5, hover_color = "white", command = useEraser)
eraser.place(x = 115, y = 5)

#Text:

def size_select(val):
    global textSize
    textSize = int(val)

def font_select(val):
    global textFont
    textFont = val

def toggle2(button):
    button.configure(fg_color = "white", border_color = "CadetBlue3", border_width = 1)
    for item in [italics, underline, bold]:
        if item != button:
            untoggle2(item)

def untoggle2(button):
    button.configure(fg_color = "gray92", border_color = "gray92")

def useText():
        global state, textFrame, italics, bold, underline, available_fonts
        state = "text"
        if isToggled(text):
            untoggle(text)
        else:
            toggle(text)
            textFrame = Frame(root,height = 80, width = 1000, bg = "gray92")
            textFrame.place(x = 370, y = 195)
            ital_image = customtkinter.CTkImage(Image.open("Italics.png"))
            italics = customtkinter.CTkButton(textFrame, fg_color = "transparent", text = "", image = ital_image, width = 5, hover_color = "white", command = useItal)
            italics.place(x = 25, y = 15)
            bold_image = customtkinter.CTkImage(Image.open("bold.png"))
            bold = customtkinter.CTkButton(textFrame, fg_color = "transparent", text = "", image = bold_image, width = 5, hover_color = "white", command = useBold)
            bold.place(x = 75, y = 15)
            und_image = customtkinter.CTkImage(Image.open("underline.png"), size = (25,25))
            underline = customtkinter.CTkButton(textFrame, fg_color = "transparent", text = "", image = und_image, width = 5, hover_color = "white", command = useUnderline)
            underline.place(x = 125, y = 15)
            sizeLabel = customtkinter.CTkLabel(textFrame, text = "Size:", font = ("Lucidia Bright", 17), text_color = "black")
            sizeLabel.place(x = 210, y = 18)
            sizes = ['8','9','10','11','12','13','14','16','18','20']
            sizeSelect = customtkinter.CTkOptionMenu(textFrame, values=sizes, command = size_select, width = 90)
            sizeSelect.place(x = 260, y = 18)
            sizeSelect.set('12')
            fontLabel = customtkinter.CTkLabel(textFrame, text = "Font:", font = ("Lucidia Bright", 17), text_color = "black")
            fontLabel.place(x = 390, y = 18)
            fontSelect = customtkinter.CTkOptionMenu(textFrame, values=available_fonts, command = font_select)
            fontSelect.place(x = 450, y = 18)
            fontSelect.set('Arial')

def useItal():
    global style
    if isToggled(italics):
        style = ''
        untoggle2(italics)
    else:
        style = 'italic'
        toggle2(italics)

def useBold():
    global style
    if isToggled(bold):
        style = ''
        untoggle2(bold)
    else:
        style = 'bold'
        toggle2(bold)

def useUnderline():
    global style
    if isToggled(underline):
        style = ''
        untoggle2(underline)
    else:
        style = 'underline'
        toggle2(underline)

text_image = customtkinter.CTkImage(Image.open("text.png"), size = (27,27))
text = customtkinter.CTkButton(kit, fg_color = "transparent", text = "", image = text_image, width = 5, hover_color = "white", command = useText)
text.place(x = 5, y = 55)

#Image:
def useImage():
    global state
    state = "image"
    toggle(image)

image_image = customtkinter.CTkImage(Image.open("image.png"), size = (27,27))
image = customtkinter.CTkButton(kit, fg_color = "transparent", text = "", image = image_image, width = 5, hover_color = "white", command = useImage)
image.place(x = 60, y = 55)

#Dropper:
def useDrop():
        global state
        state = "color_picker"
        if isToggled(drop):
            untoggle(drop)
        else:
            toggle(drop)

drop_image = customtkinter.CTkImage(Image.open("dropper.png"), size = (27,27))
drop = customtkinter.CTkButton(kit, fg_color = "transparent", text = "", image = drop_image, width = 5, hover_color = "white", command = useDrop)
drop.place(x = 115, y = 55)

#Shapes:
shapeFrame = Frame(tools, height = 140, width = 250, bg = "gray87")
shapeFrame.place(x = 665, y = 5)

shapeLabel = customtkinter.CTkLabel(shapeFrame, text = "Shapes", font = ("Lucidia Bright", 17), text_color = "black")
shapeLabel.place(x = 80, y = 25, anchor = W)

def shapeChoice(choice):
    global state
    state = choice
    for item in kit.winfo_children():
        untoggle(item)


shapes = ["Line", "Rhombus", "Rectangle", "Triangle", "Ellipse"]
shapeSelect = customtkinter.CTkOptionMenu(shapeFrame, values=shapes, command = shapeChoice)
shapeSelect.place(x=43,y=69,anchor = W)

border2 = Frame(tools,height = 95, width = 2, bg="gray78")
border2.place(x = 690, y = 20)

#Colours:
colFrame = Frame(tools, height = 140, width = 105, bg = "gray87")
colFrame.place(x = 925, y = 5)

def ask_color():
    global drawColor
    pick_color = AskColor() # open the color picker
    color = pick_color.get() # get the color string
    colChoice.configure(fg_color=color)
    drawColor = color

colPickImage = customtkinter.CTkImage(Image.open("colorpick.png"), size = (74,65))
colPick = customtkinter.CTkButton(colFrame, fg_color = "transparent", text = "", image = colPickImage, width = 5, hover = False, command = ask_color)
colPick.place(x=-2, y=2)
colChoice = customtkinter.CTkFrame(colFrame, border_color="black", border_width = 2,fg_color= drawColor, width = 35, height = 14, bg_color="gray87")
colChoice.place(x=25, y=76)

border3 = Frame(tools,height = 95, width = 2, bg="gray78")
border3.place(x = 920, y = 20)

#Thickness:
thickFrame = Frame(tools, height = 140, width = 200, bg = "gray87")
thickFrame.place(x = 1035, y = 5)

thickLabel = customtkinter.CTkLabel(thickFrame, text = "Thickness", font = ("Lucidia Bright", 17), text_color = "black")
thickLabel.place(x = 30, y = 25, anchor = W)

def thick_sliding(val):
    global lineWidth
    if val == 1:
        lineWidth = val
    else:
        lineWidth = 1 + val

thickSlide = customtkinter.CTkSlider(thickFrame, from_ = 1, to = 20, command = thick_sliding, width = 110, height = 20, number_of_steps = 10)
thickSlide.set(1)
thickSlide.place(x= 15, y = 50)

#---Actions

def click(event):
    global start_x, start_y, image_id, state
    global selection_start, selection_rectangle
    global drawColor
    global changed_width, changed_height

    if state in shapes: 
        start_x, start_y = event.x, event.y
    elif state == "text":
        start_x, start_y = event.x, event.y
        text_entry(event.x, event.y)
    elif state == "image":
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if image_path:
            img = Image.open(image_path)
            img.thumbnail((200, 200))  # Resize image to fit within 200x200 pixels
            img = ImageTk.PhotoImage(img)
            start_x, start_y = event.x, event.y
            image_id = canvas.create_image(start_x, start_y, anchor=NW, image=img)
            undo_stack.append(("image", image_id, (start_x, start_y), img))
            redo_stack.clear()
            canvas.image = img
            toggle(pencil)
            state = "draw"
    if state == "color_picker":
        x, y = event.x, event.y
        color = canvas.winfo_rgb(canvas['bg'])  # Default to background color
        try:
            item = canvas.find_closest(x, y)
            color = canvas.itemcget(item, "fill")  # Get color of the closest item
            if color == "":
                color = canvas['bg']
        except Exception as e:
            print("Error:", e)
        drawColor = color
        colChoice.configure(fg_color=drawColor)
        toggle(pencil)
        state = "draw"

def motion(event):
    global prevPoint
    global currPoint
    global lineWidth
    global state
    global shape_id, start_x, start_y
    global drawColor

    if state == "draw": 
        x = event.x
        y = event.y
        currPoint = [x,y]
        if prevPoint != [0,0]:
            drawing = canvas.create_polygon(prevPoint[0], prevPoint[1], currPoint[0], currPoint[1], fill = drawColor, outline = drawColor, width = lineWidth)
            drawMark.append((drawing,(prevPoint[0], prevPoint[1], currPoint[0], currPoint[1])))
            redo_stack.clear()
            if penciled:
                pencilMark.append(drawing)        
        prevPoint = currPoint

    elif state in shapes:
        canvas.delete(shape_id)
        shape_id = None
        if state == "Line":
            shape_id = canvas.create_line(start_x, start_y, event.x, event.y, fill=drawColor, width=lineWidth)
        elif state == "Rectangle":
            x0, y0 = start_x, start_y
            x1, y1 = event.x, event.y
            shape_id = canvas.create_rectangle(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), outline=drawColor, width=lineWidth)
        elif state == "Ellipse":
            shape_id = canvas.create_oval(start_x, start_y, event.x, event.y, outline=drawColor, width=lineWidth)
        elif state == "Rhombus":
            mid_x = (start_x + event.x) // 2
            mid_y = (start_y + event.y) // 2
            shape_id = canvas.create_polygon(start_x, mid_y, mid_x, start_y, event.x, mid_y, mid_x, event.y, outline=drawColor, fill="", width=lineWidth)
        elif state == "Triangle":
            shape_id = canvas.create_polygon(start_x, event.y, (start_x + event.x) // 2, start_y, event.x, event.y, outline=drawColor, fill="", width=lineWidth)

def release(event):
    global prevPoint, shape_id
    global selection_start, selection_end, selected_image
    global drawMark
    global changed_width, changed_height

    if state == "draw":
        undo_stack.append((state, drawMark.copy(), drawColor, lineWidth))
        drawMark = []
        prevPoint = [0,0]
    elif state in shapes:
        shape_action = (state, shape_id, (start_x, start_y, event.x, event.y), drawColor, lineWidth)
        undo_stack.append(shape_action)
        redo_stack.clear()
        shape_id = None 

def draw_shape(shape, coords, color, sh_width):
    
    if shape == "Line":
        return canvas.create_line(coords, fill=color, width=sh_width)
    elif shape == "Rectangle":
        return canvas.create_rectangle(coords, outline=color, width=sh_width)
    elif shape == "Ellipse":
        return canvas.create_oval(coords, outline=color, width=sh_width)
    elif shape == "Rhombus":
        mid_x = (coords[0] + coords[2]) // 2
        mid_y = (coords[1] + coords[3]) // 2
        return canvas.create_polygon(coords[0], mid_y, mid_x, coords[1], coords[2], mid_y, mid_x, coords[3], outline=color, fill="", width=sh_width)
    elif shape == "Triangle":
        return canvas.create_polygon(coords[0], coords[3], (coords[0] + coords[2]) // 2, coords[1], coords[2], coords[3], outline=color, fill="", width=sh_width)

def text_entry(x, y):
    global text_input
    text_input = Entry(canvas)
    text_input.place(x=x, y=y)
    text_input.focus_set()
    text_input.bind("<Return>", place_text)
    canvas.bind("<Button-1>", place_text)

def place_text(event):
    global changed_width, changed_height
    global start_x, start_y
    text = text_input.get()
    text_id = canvas.create_text(start_x, start_y, text=text, fill=drawColor, font=(textFont, textSize, style))
    undo_stack.append(("text", text_id, (start_x, start_y), text, drawColor, (textFont, textSize, style)))
    redo_stack.clear()
    text_input.destroy()
    canvas.unbind("<Button-1>")
    canvas.bind("<ButtonPress-1>", click)

canvas.bind("<ButtonPress-1>", click)
canvas.bind("<B1-Motion>",motion)
canvas.bind("<ButtonRelease-1>", release)

root.resizable(False , False)
root.mainloop()