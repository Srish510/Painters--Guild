import tkinter as tk

root = tk.Tk()

root.geometry("1200x1200")
root.title("GUI Practice")


frame1 = tk.Frame(root , height=100 , width=1200 , bg="red")
frame1.grid(row=0 , column=0)

frame2 = tk.Frame(root , height=500 , width=1200 , bg="yellow")
frame2.grid(row=1 , column=0)


root.resizable(False , False)

root.mainloop()
