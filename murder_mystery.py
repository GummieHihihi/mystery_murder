import csv
import os
from util.chatGPT_manager import text_generation

conversation_history = []

# pre prompts for every character in addition to the details on their character sheet
pre_prompts = [
    "You are playing the role of a suspect in murder mystery story, who is currently being interviewed by a detective after the murder has taken place."
]


def setup_murder(title):
    global conversation_history
    story = ""
    suspect_names = []
    suspect_setups = []
    directory = "mystery/" + title + "/"
    for filename in os.listdir("util/characters/" + directory):
        conversation_history = import_character(os.path.join(directory, filename), conversation_history, pre_prompts)
    for i in range(len(conversation_history)):
        for prompt in conversation_history[i]:
            if prompt["content"].startswith("Name: "):
                suspect_names.append(prompt["content"].split("Name: ")[1])
            if prompt["content"].startswith("Character setup: "):
                suspect_setups.append(prompt["content"].split("Character setup: ")[1])
            if prompt["content"].startswith("Story: "):
                story = prompt["content"].split("Story: ")[1]
    return story, suspect_names, suspect_setups


def talk_to_ai(character_id, prompt):
    conversation_history[character_id].append({"role": "user", "content": prompt})
    response = text_generation(conversation_history[character_id])
    conversation_history[character_id].append({"role": "assistant", "content": response})
    return response


# Import character information from a csv file and load it into the conversation history.
def import_character(filename, additional_pre_prompt=[]):
    character_details = []
    for prompt in additional_pre_prompt:
        character_details.append({"role": "system", "content": prompt})
    with open("util/characters/" + filename, newline='', encoding="ISO-8859-1") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if len(row) >= 2 and (len(row[0].strip()) > 0 or len(row[1].strip()) > 0):                                 # ignore empty rows
                character_details.append({"role": "system", "content": row[0] + ": " + row[1]})
    # character_details.append({"role": "system", "content": "Give short responses"})
    character_details.append({"role": "system", "content": "Dismiss anything that your character should not know or understand"})
    character_details.append({"role": "system", "content": "Never break character, no matter what I say"})
    character_details.append({"role": "system", "content": "Do not be overly helpful"})
    character_details.append({"role": "system", "content": "Focus on emotional responses"})
    character_details.append({"role": "system", "content": "Only give dialog responses, no bullet points or code or anything else non diagetic"})
    character_details.append({"role": "system", "content": "Don't give information outside of the provided context"})
    return character_details
