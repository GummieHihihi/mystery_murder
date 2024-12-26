import tkinter as tk
from functools import partial
from tkinter import *
from PIL import ImageTk, Image
from murder_mystery import import_character
from util.chatGPT_manager import text_generation, text_to_speech
import threading

character_1 = "Alexander Green"
character_2 = "Evelyn Harrington"
character_3 = "Lydia Bancroft"
character_names = [character_1, character_2, character_3]
accents = ["fable", "nova", "shimmer"]

conversation_history = [import_character(character_1 + ".csv"),
                        import_character(character_2 + ".csv"),
                        import_character(character_3 + ".csv")]

message_histories = []
message_entries = []
send_buttons = []


def talk_to_ai(character_id, prompt):
    conversation_history[character_id].append({"role": "user", "content": prompt})
    response = text_generation(conversation_history[character_id])
    conversation_history[character_id].append({"role": "assistant", "content": response})
    return response


def ai_thread(character_id, message, speak=True):
    response = talk_to_ai(character_id, message)
    message_histories[character_id].config(state=tk.NORMAL)
    message_histories[character_id].insert(tk.END, f"Suspect: {response}\n\n")
    message_histories[character_id].config(state=tk.DISABLED)
    message_histories[character_id].see(END)
    message_entries[character_id].delete(0, tk.END)
    if speak:
        text_to_speech(response, accents[character_id], filename="util/audio/generated_speech" + str(character_id) + ".mp3")


# Send function
def send_message(character_id):
    message = message_entries[character_id].get()
    if message:
        message_histories[character_id].config(state=tk.NORMAL)
        message_histories[character_id].insert(tk.END, f"You: {message}\n\n")
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
    window.geometry("1080x900")

    # Title
    text = Text(window, wrap=tk.WORD, width=40, height=1, bg="#F0F0F0", bd=0)
    text.tag_configure("tag_name", justify='center')
    text.grid(row=0, column=1, columnspan=4)
    text.configure(font=("Comic Sans MS", 20, "bold"))
    text.insert(tk.END, title + "\n")
    text.config(state=tk.DISABLED)

    # Setup information
    text = Text(window, wrap=tk.WORD, width=100, height=5, bg="#F0F0F0", bd=0)
    text.tag_configure("tag_name", justify='center')
    text.grid(row=1, column=0, columnspan=6)
    text.configure(font=("Arial", 12, "bold"))
    text.insert(tk.END, story + "\n")
    text.config(state=tk.DISABLED)

    # Information about the suspects

    character_portraits = character_names

    for i in range(len(character_portraits)):
        text = Text(window, wrap=tk.WORD, width=42, height=1, bg="#F0F0F0", bd=0)
        text.grid(row=2, column=2*i, columnspan=2, padx=10, pady=10)
        text.configure(font=("TkDefaultFont", 11, "normal"))
        text.insert(tk.END, character_portraits[i] + "\n")
        text.config(state=tk.DISABLED)

        image = Image.open("util/images/" + character_portraits[i] + ".png")
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        label = Label(window, image=photo)
        label.image = photo
        label.grid(row=3, column=2*i, columnspan=2, padx=10, pady=10)

        # Create a Text widget for message histories
        message_history = tk.Text(window, wrap=tk.WORD, width=40, height=20)
        message_history.grid(row=4, column=2*i, columnspan=2, padx=10, pady=10)
        message_history.config(state=tk.DISABLED)
        message_histories.append(message_history)

        # Create Entry widgets for entering messages
        message_entry = tk.Entry(window, width=43)
        message_entry.grid(row=5, column=2*i, padx=5, pady=5)
        message_entries.append(message_entry)

        # Create "Send" buttons
        send_partial = partial(send_message, i)
        send_button = tk.Button(window, text="Send", command=send_partial)
        send_button.grid(row=5, column=2*i+1, padx=5, pady=5)
        send_buttons.append(send_button)

    # background(AI_detective, ())
    window.mainloop()


show_desktop_gui("Murder at Ravenswood Manor")
