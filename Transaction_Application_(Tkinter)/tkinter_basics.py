from tkinter import ttk, Tk, GROOVE

root = Tk()

""" 
This is another way of doing it:
myLabel = ttk.Label(root, text="This is a test label")
myLabel.pack()
"""


# def button_clicked():
#     print(my_name.get())

# my_name = ttk.Entry(root)
# my_name.pack()

# ttk.Button(root, text="Click me", command=button_clicked).pack()

# 'grid' is more flexible than 'pack'
# Frames
frame_header = ttk.Frame(root)
frame_header.pack()
frame_header.config(relief=GROOVE, padding=(50,15))
ttk.Label(frame_header, text="This is a test label").grid(row=0,column=0)

frame_second = ttk.Frame(root)
frame_second.pack()
ttk.Label(frame_second, text="This is a second test").grid(row=1, column=2)



root.mainloop()