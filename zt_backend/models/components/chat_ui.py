from zt_backend.models.components.text_input import TextInput
from zt_backend.models.components.button import Button
from zt_backend.models.components.text import Text
from zt_backend.models.components.slider import Slider
from zt_backend.models.components.card import Card
from zt_backend.models.components.layout import Row, Layout
from zt_backend.models.state.state import state
import openai
import logging

class CustomError(Exception):
    """Custom exception class for user-friendly error messages."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

def chat_ui(api_key=""):

    # Initialize state
    zt_state = state()

    # Ensure state for message history
    if "message_history" not in zt_state:
        zt_state["message_history"] = []


    if api_key:
        openai.api_key = api_key
    else:
        raise CustomError("Invalid API Key: Please provide a valid API key.")
    # UI Components
    temperature_slider = Slider(id="temperature_sliders", min=0, max=1, step=0.01, value=0.5, label="Temperature")
    generate_button = Button(id="generate_buttons", text="Generate")
    prompt_input = TextInput(id="prompt_inputs", label="Enter your prompt", placeholder="Type something...")
    clear_chat = Button(id='clear_chats', text='Clear Chat')

    # Function to add a message to the history
    def add_message_to_history(role, content):
        zt_state["message_history"].append({"role": role, "content": content})
        prompt_input.value = ''  # Clear the prompt input after adding message to history


    def generate_text(prompt, temperature):
        # Prepare the conversation history for the API request
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        for message in zt_state["message_history"]:
            messages.append({"role": message["role"], "content": message["content"]})

        # Add the current prompt to the conversation
        messages.append({"role": "user", "content": prompt})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=temperature
            )
            generated_content = response.choices[0].message['content'].strip()
            return generated_content
        except Exception as e:
            return f"An error occurred: {e}"

    def update_chat_ui():
        try:
            # Initialize the list for cards representing each message in history
            cards_for_messages = []

            # Create cards for each message in history
            for index, message in enumerate(zt_state["message_history"]):
                header_text = "User Input:" if message["role"] == "user" else "GPT Output:"
                header_color = "primary" if message["role"] == "user" else "secondary"
                card_color = "blue" if message["role"] == "user" else "green"

                message_header = Text(id=f"header_{index}", text=header_text, color=header_color)
                message_text = Text(id=f"message_{index}", text=message["content"], color="info")

                # Create a new card for the message and append to the cards list
                message_card = Card(
                    id=f"message_card_{index}",
                    childComponents=[message_header.id, message_text.id],
                    color=card_color,
                    width=1200
                )
                cards_for_messages.append(Row([message_card.id]))

            # UI Components rows for user interaction
            user_interaction_rows = [
                Row([prompt_input.id]),
                Row([temperature_slider.id]),
                Row([generate_button.id]),
                Row([clear_chat.id])
            ]

            # Combine chat history cards and user interaction rows
            layout_rows = cards_for_messages + user_interaction_rows

            # Update the layout with the new rows
            layout = Layout(rows=layout_rows)
            # Assuming there's a mechanism to render the layout, if needed
        except Exception as e:
            logging.error(f"An error occurred while updating the chat UI: {e}")

    def gen():
        user_prompt = prompt_input.value
        generated_response = generate_text(user_prompt, temperature_slider.value)
        add_message_to_history("user", user_prompt)
        add_message_to_history("assistant", generated_response)
        update_chat_ui()


    # Clear chat button event handler
    if clear_chat.value:
        zt_state["message_history"] = []
        update_chat_ui()

    # Generate button event handler
    if generate_button.value or prompt_input.value:
        gen()


    update_chat_ui()