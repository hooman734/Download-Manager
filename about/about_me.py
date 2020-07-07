from tkinter import Toplevel, LabelFrame, Label, X, CENTER


def about():
    about_me = Toplevel()
    about_me.geometry("300x150")
    about_me.title("About...")
    frame = LabelFrame(about_me, text='about the developer:')
    frame.pack(fill=X, expand=1)
    Label(frame, justify=CENTER, text="""
        .: Hooman Hesamyan :.
        
        Tell: +374-77-281-774
        E-mail: hesamyan@gmail.com
        Web: hooman.hesamian.com
    
    """).pack(fill=X, expand=1)
