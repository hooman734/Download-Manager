import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from pySmartDL import SmartDL
from pathlib import Path
import threading

# define main window
root = tk.Tk()
root.title("Download Manager")
root.geometry("700x300")

# define parameters
input_link = tk.StringVar()
status_message = tk.StringVar()
speed_message = tk.StringVar()
dest_message = tk.StringVar()
size_message = tk.StringVar()
time_message = tk.StringVar()


# define functions
# handle download
def download(__url__):
    global status_message
    global speed_message
    global dest_message
    global size_message
    global time_message
    global progress

    def do_download():
        show_progress = True
        url = __url__
        dest = Path.home() / "Downloads" / "Hooman-Downloader"
        dest.mkdir(mode=0o777, parents=True, exist_ok=True)
        dest = str(dest)
        obj = SmartDL(url, dest)
        status_message.set("Status: " + obj.get_status())
        # threading.Thread(target=obj.start()).start()
        obj.start()
        print("--------------->>>>", obj.get_status())

        status_message.set("Status: " + obj.get_status())
        speed_message.set("Speed: " + obj.get_speed(human=True))
        dest_message.set("Destination: " + obj.get_dest())
        size_message.set("File Size: " + obj.get_final_filesize(human=True))
        time_message.set("Elapsed Time: " + str(obj.get_dl_time(human=True)))
        progress['value'] = 100 * obj.get_progress()
        time.sleep(0.3)
        print(obj.get_status())
        root.update_idletasks()

        # print(obj.get_progress_bar(length=40))

    if len(__url__) == 0:
        button_download.flash()
    else:
        threading.Thread(target=do_download).start()  # download with a new thread


# handle right click's event
def do_popup(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()


# handle copy, paste, cut, past & download
def cut(__input__):
    i = __input__
    entry_link.clipboard_clear()
    entry_link.clipboard_append(i)
    input_link.set('')


def copy(__input__):
    i = __input__
    entry_link.clipboard_clear()
    entry_link.clipboard_append(i)


def paste(__input__):
    i0 = __input__
    i1 = entry_link.clipboard_get()
    input_link.set(i0 + i1)


def paste_and_down(__input__):
    i0 = __input__
    i1 = entry_link.clipboard_get()
    input_link.set(i0 + i1)
    download(entry_link.get())
    button_download.flash()
    button_download['state'] = DISABLED


def clear_reset():
    input_link.set('')
    button_download['state'] = NORMAL


def start_downloading():
    download(entry_link.get())
    button_download.flash()
    button_download['state'] = DISABLED


# define menu bar
app_menu = tk.Menu(root)

# configure root with our menu
root.config(menu=app_menu)

# define and scaffold sub-menu's in our application's menu
menu_file = tk.Menu(app_menu, tearoff=False)
app_menu.add_cascade(label="File", menu=menu_file)
#
menu_edit = tk.Menu(app_menu, tearoff=False)
app_menu.add_cascade(label="Edit", menu=menu_edit)
#
menu_help = tk.Menu(app_menu, tearoff=False)
app_menu.add_cascade(label="Help", menu=menu_help)

# define each sub-menu its title and responsibility
menu_file.add_command(label="first command")
menu_file.add_separator()
menu_file.add_command(label="Exit", command=root.destroy)
#
menu_edit.add_command(label="Cut", command=lambda: cut(entry_link.get()))
menu_edit.add_command(label="Copy", command=lambda: copy(entry_link.get()))
menu_edit.add_command(label="Paste", command=lambda: paste(entry_link.get()))
menu_edit.add_command(label="Paste & Download", command=lambda: paste_and_down(entry_link.get()))
#
menu_help.add_separator()
menu_help.add_command(label="About")

# define and scaffold status frame
frame_status = tk.LabelFrame(root, text="Information", relief=SUNKEN, borderwidth=5)
frame_status.pack(fill=BOTH, expand=1)

# define and scaffold input frame
frame_input = tk.Frame(root, relief=RIDGE, borderwidth=5)
frame_input.pack(fill=BOTH, expand=1)

# define and scaffold action frame
frame_action = tk.LabelFrame(root, text="Take action", relief=RAISED, borderwidth=5)
frame_action.pack(fill=BOTH, expand=1, side=BOTTOM)

# define and scaffold elements
# status labels
label_status = tk.Label(frame_status, textvariable=status_message, justify=LEFT)
label_status.grid(row=1, column=0, sticky=W)
label_speed = tk.Label(frame_status, textvariable=speed_message, justify=LEFT)
label_speed.grid(row=2, column=0, sticky=W)
label_size = tk.Label(frame_status, textvariable=size_message, justify=LEFT)
label_size.grid(row=3, column=0, sticky=W)
label_time = tk.Label(frame_status, textvariable=time_message, justify=LEFT)
label_time.grid(row=4, column=0, sticky=W)
label_destination = tk.Label(frame_status, textvariable=dest_message, justify=LEFT)
label_destination.grid(row=5, column=0, sticky=W)
progress = ttk.Progressbar(frame_status, orient=HORIZONTAL, length=700, mode='determinate')
progress.grid(row=6, column=0, sticky=W + E)

# widgets
label_link = tk.Label(frame_input, text=".. Input a link here to start downloading...", font=('Times', 14))
label_link.pack(fill=X, side=TOP, pady=10)
entry_link = tk.Entry(frame_input, textvariable=input_link, font=('Mono', 12))
entry_link.pack(fill=X, expand=1, side=LEFT, pady=5, padx=10)
button_download = tk.Button(frame_action, text="Start Downloading!", command=lambda: start_downloading(),
                            width=30)
button_download.pack(side=LEFT, padx=20)
button_clear = tk.Button(frame_action, text="Clear & Reset!", command=lambda: clear_reset(), width=30)
button_clear.pack(side=RIGHT, padx=20)

# define right click menu
m = tk.Menu(root, tearoff=0)
m.add_command(label="Cut", command=lambda: cut(entry_link.get()))
m.add_command(label="Copy", command=lambda: copy(entry_link.get()))
m.add_command(label="Paste", command=lambda: paste(entry_link.get()))
m.add_command(label="Paste & Down.", command=lambda: paste_and_down(entry_link.get()))
m.add_separator()
m.add_command(label="Cancel!", command=m.forget)
entry_link.bind("<Button-3>", do_popup)

# main loop
root.mainloop()
