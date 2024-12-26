import streamlit
from murder_mystery import setup_murder, talk_to_ai


def show_streamlit_gui(title):
    streamlit.set_page_config(page_title="Mystery GPT Demo", layout="wide")
    streamlit.header(title)

    css = '''
    <style>
        section.main > div {max-width:1200pt;min-width:1200pt}
    </style>
    '''
    streamlit.markdown(css, unsafe_allow_html=True)

    story, suspect_names, suspect_setups = setup_murder(title)

    streamlit.write(story)
    streamlit.write("")

    def update_suspect1_prompt():
        prompt = streamlit.session_state.Suspect1_prompt
        streamlit.session_state.Suspect1_text_area += "You: " + prompt + "\n\n"
        streamlit.session_state.Suspect1_prompt = ""
        response = talk_to_ai(0, prompt)
        streamlit.session_state.Suspect1_text_area += "Suspect: " + response + "\n\n"

    def update_suspect2_prompt():
        prompt = streamlit.session_state.Suspect2_prompt
        streamlit.session_state.Suspect2_text_area += "You: " + prompt + "\n\n"
        streamlit.session_state.Suspect2_prompt = ""
        response = talk_to_ai(1, prompt)
        streamlit.session_state.Suspect2_text_area += "Suspect: " + response + "\n\n"

    def update_suspect3_prompt():
        prompt = streamlit.session_state.Suspect3_prompt
        streamlit.session_state.Suspect3_text_area += "You: " + prompt + "\n\n"
        streamlit.session_state.Suspect3_prompt = ""
        response = talk_to_ai(2, prompt)
        streamlit.session_state.Suspect3_text_area += "Suspect: " + response + "\n\n"

    col1, col2, col3 = streamlit.columns(3)
    with col1:
        i = 0
        streamlit.write("**" + suspect_names[i] + "**")
        streamlit.write(suspect_setups[i])
        image_location = "util/images/mystery/" + title + "/" + suspect_names[i] + ".png"
        streamlit.image(image=image_location, width=330)
        streamlit.text_area(label="Suspect1_text_area", label_visibility='collapsed', placeholder="", key="Suspect1_text_area", height=300)
        streamlit.text_input(label="Suspect1_prompt", label_visibility='collapsed',  placeholder="Write a message here...", key="Suspect1_prompt")
        streamlit.button("Send", type='secondary', on_click=update_suspect1_prompt, key="Suspect1_send")

    with col2:
        i = 1
        streamlit.write("**" + suspect_names[i] + "**")
        streamlit.write(suspect_setups[i])
        image_location = "util/images/mystery/" + title + "/" + suspect_names[i] + ".png"
        streamlit.image(image=image_location, width=330)
        streamlit.text_area(label="Suspect2_text_area", label_visibility='collapsed', placeholder="", key="Suspect2_text_area", height=300)
        streamlit.text_input(label="Suspect2_prompt", label_visibility='collapsed',  placeholder="Write a message here...", key="Suspect2_prompt")
        streamlit.button("Send", type='secondary', on_click=update_suspect2_prompt, key="Suspect2_send")

    with col3:
        i = 2
        streamlit.write("**" + suspect_names[i] + "**")
        streamlit.write(suspect_setups[i])
        image_location = "util/images/mystery/" + title + "/" + suspect_names[i] + ".png"
        streamlit.image(image=image_location, width=330)
        streamlit.text_area(label="Suspect3_text_area", label_visibility='collapsed', placeholder="", key="Suspect3_text_area", height=300)
        streamlit.text_input(label="Suspect3_prompt", label_visibility='collapsed',  placeholder="Write a message here...", key="Suspect3_prompt")
        streamlit.button("Send", type='secondary', on_click=update_suspect3_prompt, key="Suspect3_send")

    url = "https://docs.google.com/forms/d/1t048rYHKrYLZVTbXuMR72rikDZIAlJjrIh1SvJyRAk0"
    streamlit.write("Player Feedback Form [link](%s)" % url)
    streamlit.markdown("Player Feedback Form [link](%s)" % url)


show_streamlit_gui("Murder at Ravenswood Manor")
