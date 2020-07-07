import time
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from pySmartDL import SmartDL
from pathlib import Path
import threading
import subprocess
import os

# define main window
root = tk.Tk()
root.title("AMIR Download Manager")
root.geometry("700x400")


# define parameters
dl_object = ''
default_browser = ''
input_link = tk.StringVar()
status_message = tk.StringVar()
speed_message = tk.StringVar()
dest_message = tk.StringVar()
size_message = tk.StringVar()
time_message = tk.StringVar()
dest = Path.home() / "Downloads" / "AMIR-Downloader"
dest.mkdir(mode=0o777, parents=True, exist_ok=True)  # make working directory


# define functions
def terminate(obj):
    obj.stop()
    button_pause['state'] = DISABLED
    button_resume['state'] = DISABLED


# handle download
def download(__url__):
    global status_message
    global speed_message
    global dest_message
    global size_message
    global time_message
    global progress
    global dest
    global dl_object

    url = __url__
    dest = str(dest)

    button_stop['command'] = lambda: terminate(dl_object)
    button_stop['state'] = NORMAL
    button_pause['command'] = lambda: dl_object.pause()
    button_pause['state'] = NORMAL
    button_resume['command'] = lambda: dl_object.unpause()
    button_resume['state'] = NORMAL

    def do_download(sem):
        with sem:
            try:
                dl_object.start()
            except Exception as e:
                print(f"------> {e}")
                print(f"object error ---> {dl_object.get_errors()}")
                status_message.set(f"Status: {e}")
                root.update_idletasks()

    def show_progress(sem):
        with sem:
            time.sleep(1)
            start_time = time.perf_counter()
            while not dl_object.isFinished() and len(dl_object.get_errors()) == 0:
                status_message.set(f"Status: {dl_object.get_status()}")
                speed_message.set(f"Speed: {dl_object.get_speed(human=True)}")
                dest_message.set(f"Working directory: {dest}")
                size_message.set(f"Downloaded so far: {dl_object.get_dl_size(human=True)}")
                time_message.set(f"Elapsed Time: {round(time.perf_counter() - start_time, 1)}" if dl_object.get_status() != 'paused' else '-')
                progress['value'] = 100 * dl_object.get_progress()
                time.sleep(0.2)
                root.update_idletasks()
            if len(dl_object.get_errors()) == 0:
                start_point = time.perf_counter()
                while time.perf_counter() - start_point < 5:
                    status_message.set(f"Status: {dl_object.get_status()}")
                    speed_message.set(f"Speed: {dl_object.get_speed(human=True)}")
                    dest_message.set(f"Saved in: {dl_object.get_dest()}")
                    size_message.set(f"Total File Size: {dl_object.get_final_filesize(human=True)}")
                    time_message.set(f"Total Time: {str(dl_object.get_dl_time(human=True))}")
                    progress['value'] = 100 * dl_object.get_progress()
                    time.sleep(0.2)
                    root.update_idletasks()
            else:
                status_message.set(f"Status: Failed to download!")
                speed_message.set(f"Reason: {dl_object.get_errors()[0]}")
                root.update_idletasks()

    if len(url) == 0:
        button_download.flash()
    else:
        try:
            dl_object = SmartDL(url, dest)
        except Exception as e:
            print(f"Error in {e}")
            status_message.set(f"Status: {e}")
            root.update_idletasks()
        semaphore = threading.Semaphore(2)
        threading.Thread(target=do_download, args=(semaphore,)).start()
        threading.Thread(target=show_progress, args=(semaphore,)).start()


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


def browsing():
    global default_browser
    if default_browser == '':
        default_browser = subprocess.run(["xdg-mime", "query", "default", "inode/directory"],
                                         stdout=subprocess.PIPE).stdout.decode('utf-8').split('.')[-2].lower()

    threading.Thread(target=os.system, args=(f"{default_browser} {dest}",)).start()


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
menu_download = tk.Menu(app_menu, tearoff=False)
app_menu.add_cascade(label="Download", menu=menu_download)
#
menu_help = tk.Menu(app_menu, tearoff=False)
app_menu.add_cascade(label="Help", menu=menu_help)

# define each sub-menu its title and responsibility
menu_file.add_command(label="Clear & Reset", command=clear_reset)
menu_file.add_separator()
menu_file.add_command(label="Exit", command=root.destroy)
#
menu_edit.add_command(label="Cut", command=lambda: cut(entry_link.get()))
menu_edit.add_command(label="Copy", command=lambda: copy(entry_link.get()))
menu_edit.add_command(label="Paste", command=lambda: paste(entry_link.get()))
menu_edit.add_command(label="Paste & Download", command=lambda: paste_and_down(entry_link.get()))
#
menu_download.add_command(label="Stop!", command=lambda: terminate(dl_object))
menu_download.add_command(label="Pause!", command=lambda: dl_object.pause())
menu_download.add_command(label="Resume!", command=lambda: dl_object.unpause())
#
menu_help.add_separator()
menu_help.add_command(label="About")

# define and scaffold progress frame
frame_progress = tk.Frame(root, relief=GROOVE, borderwidth=5)
frame_progress.pack(fill=BOTH, expand=1)

# define and scaffold download operations frame
frame_dl_op = tk.Frame(root, relief=GROOVE, borderwidth=5)
frame_dl_op.pack(fill=BOTH, expand=1)

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

# progress bar
progress = ttk.Progressbar(frame_progress, orient=HORIZONTAL, length=700, mode='determinate')
progress.pack(fill=X, expand=1)

# widgets
label_link = tk.Label(frame_input, text=".. Input a link here to start downloading...", font=('Times', 14))
label_link.pack(fill=X, side=TOP, pady=10)
entry_link = tk.Entry(frame_input, textvariable=input_link, font=('Mono', 12))
entry_link.pack(fill=X, expand=1, side=LEFT, pady=5, padx=10)
button_download = tk.Button(frame_action, text="Start Downloading!", command=lambda: start_downloading(),
                            width=20, fg="green")
button_download.pack(side=LEFT, padx=10)
button_clear = tk.Button(frame_action, text="Clear & Reset!", command=lambda: clear_reset(), width=20, fg="#8f0926")
button_clear.pack(side=RIGHT, padx=10)
button_open = tk.Button(frame_action, text="Open Downloads!", command=lambda: browsing(), width=20, fg="#12098f")
button_open.pack(fill=X, expand=1, side=BOTTOM, padx=10)

# define and scaffold download operation keys
button_resume = tk.Button(frame_dl_op, state=DISABLED, text="Resume!", width=20, fg="green")
button_resume.pack(side=LEFT, padx=10)
button_pause = tk.Button(frame_dl_op, state=DISABLED, text="Pause!", width=20, fg="#8f0926")
button_pause.pack(side=RIGHT, padx=10)
button_stop = tk.Button(frame_dl_op, state=DISABLED, text="Terminate Downloading!", width=20, fg="#12098f")
button_stop.pack(fill=X, expand=1, side=BOTTOM, padx=10)

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
