# These are like plug-ins you turn on before you start
from openai import OpenAI # Lets you talk to GPT
from dotenv import load_dotenv # Lets Python read your .env file
import os # Lets Python access your computer's variables

## Opens your .env file and loads your API key into memory
load_dotenv()

# Creates your connection to OpenAI using your key - like logging in
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_agent(user_message):
    # Sends the conversation to OpenAI and stores the response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[  # The conversation you're sending (a list of dictionaries)
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    # Digs into the response object to get just the text
    # choices[0] = first response (OpenAI can return multiple)
    # .message.content = the actual text of the reply
    return response.choices[0].message.content

def summarize_text(text):
    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": "Summarize the following text in 3 bullets"},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content
# Test it
answer = ask_agent("What are tokens used for in using openAI?")
print(answer)

print("Q2\n\n\n\n\n")
print(summarize_text(answer))

