import tkinter as tk
from functools import partial
from tkinter import *
from PIL import ImageTk, Image
from murder_mystery import import_character
from util.chatGPT_manager import text_generation, text_to_speech
import threading
from event_system import EventManager

character_1 = "Alexander Green"
character_2 = "Evelyn Harrington"
character_3 = "Lydia Bancroft"
character_4 = "Crime Scene"
character_names = [character_1, character_2, character_3, character_4]
accents = ["fable", "nova", "shimmer", "alloy"]

conversation_history = [import_character(character_1 + ".csv"),
                      import_character(character_2 + ".csv"),
                      import_character(character_3 + ".csv"),
                      import_character(character_4 + ".csv")]

event_manager = EventManager(conversation_history)
event_manager.create_event_system_structure()
event_manager.load_event_sheet("chapter1_events.csv")

message_histories = []
message_entries = []
send_buttons = []

def talk_to_ai(character_id, prompt):
    event_manager.process_message(prompt, character_id)
    conversation_history[character_id].append({"role": "user", "content": prompt})
    response = text_generation(conversation_history[character_id])
    conversation_history[character_id].append({"role": "assistant", "content": response})
    return response

def ai_thread(character_id, message, speak=True):
    response = talk_to_ai(character_id, message)
    message_histories[character_id].config(state=tk.NORMAL)
    prefix = "Crime Scene Analysis: " if character_names[character_id] == "Crime Scene" else "Suspect: "
    message_histories[character_id].insert(tk.END, f"{prefix}{response}\n\n")
    message_histories[character_id].config(state=tk.DISABLED)
    message_histories[character_id].see(END)
    message_entries[character_id].delete(0, tk.END)
    
    # Play sounds for all characters
    if speak:
        text_to_speech(response, accents[character_id], filename="util/audio/generated_speech" + str(character_id) + ".mp3")

def send_message(character_id):
    message = message_entries[character_id].get()
    if message:
        message_histories[character_id].config(state=tk.NORMAL)
        # Change the displayed text depending on the character
        prefix = "Crime Scene Analysis: " if character_names[character_id] == "Crime Scene" else "You: "
        message_histories[character_id].insert(tk.END, f"{prefix}{message}\n\n")
        message_histories[character_id].config(state=tk.DISABLED)
        message_histories[character_id].see(END)
        message_entries[character_id].delete(0, tk.END)
        background(ai_thread, (character_id, message))

def background(func, args):
    th = threading.Thread(target=func, args=args)
    th.start()

def show_desktop_gui(title):
    story = "In the quaint town of Ravenswood, a shocking murder has occurred at the historic Ravenswood Manor " \
            "during a charity ball. The victim, renowned art collector and philanthropist, Charles Vandenberg, " \
            "was found in his study, a room filled with priceless artifacts and paintings. The study door was " \
            "locked, and only two keys to the study exist. One was found on Charles' body and the other belongs " \
            "to the housekeeper Mrs. Lydia Bancroft."

    # Create the main window
    window = tk.Tk()
    window.title("Murder Mystery")
    
    # Create main frame with scrollbar
    main_frame = Frame(window)
    main_frame.pack(fill=BOTH, expand=1)
    
    # Create canvas with scrollbar
    canvas = Canvas(main_frame)
    scrollbar = Scrollbar(main_frame, orient=HORIZONTAL, command=canvas.xview)
    scrollbar.pack(side=BOTTOM, fill=X)
    
    canvas.configure(xscrollcommand=scrollbar.set)
    canvas.pack(side=LEFT, fill=BOTH, expand=1)
    
    # Create frame inside canvas for content
    content_frame = Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    # Title
    text = Text(content_frame, wrap=tk.WORD, width=40, height=1, bg="#F0F0F0", bd=0)
    text.tag_configure("tag_name", justify='center')
    text.grid(row=0, column=1, columnspan=4)
    text.configure(font=("Comic Sans MS", 18, "bold"))
    text.insert(tk.END, title + "\n")
    text.config(state=tk.DISABLED)

    # Setup information
    text = Text(content_frame, wrap=tk.WORD, width=100, height=4, bg="#F0F0F0", bd=0)
    text.tag_configure("tag_name", justify='center')
    text.grid(row=1, column=0, columnspan=6)
    text.configure(font=("Arial", 11, "bold"))
    text.insert(tk.END, story + "\n")
    text.config(state=tk.DISABLED)

    character_portraits = character_names

    for i in range(len(character_portraits)):
        text = Text(content_frame, wrap=tk.WORD, width=35, height=1, bg="#F0F0F0", bd=0)
        text.grid(row=2, column=2*i, columnspan=2, padx=5, pady=5)
        text.configure(font=("TkDefaultFont", 10, "normal"))
        text.insert(tk.END, character_portraits[i] + "\n")
        text.config(state=tk.DISABLED)

        # Load and resize images
        image = Image.open("util/images/" + character_portraits[i] + ".png")
        image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(image)
        label = Label(content_frame, image=photo)
        label.image = photo
        label.grid(row=3, column=2*i, columnspan=2, padx=5, pady=5)

        # Message history
        message_history = tk.Text(content_frame, wrap=tk.WORD, width=35, height=8)
        message_history.grid(row=4, column=2*i, columnspan=2, padx=5, pady=5)
        message_history.config(state=tk.DISABLED)
        message_histories.append(message_history)

        # Message entry - Adjust placeholder text according to character
        message_entry = tk.Entry(content_frame, width=35)
        placeholder = "Analyze crime scene..." if character_portraits[i] == "Crime Scene" else "Ask question..."
        message_entry.insert(0, placeholder)
        message_entry.bind('<FocusIn>', lambda e, entry=message_entry, ph=placeholder: 
                         on_entry_click(entry, ph))
        message_entry.bind('<FocusOut>', lambda e, entry=message_entry, ph=placeholder: 
                         on_focus_out(entry, ph))
        message_entry.grid(row=5, column=2*i, padx=2, pady=2)
        message_entries.append(message_entry)

        # Send button
        send_partial = partial(send_message, i)
        button_text = "Analyze" if character_portraits[i] == "Crime Scene" else "Send"
        send_button = tk.Button(content_frame, text=button_text, command=send_partial)
        send_button.grid(row=5, column=2*i+1, padx=2, pady=2)
        send_buttons.append(send_button)

    # Update scroll region after adding all elements
    content_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Set initial window size
    window.geometry("1000x800")
    
    window.mainloop()

# Add placeholder text handling functions
def on_entry_click(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg='black')

def on_focus_out(entry, placeholder):
    if entry.get() == '':
        entry.insert(0, placeholder)
        entry.config(fg='grey')

show_desktop_gui("Murder at Ravenswood Manor")