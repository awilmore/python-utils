#!/usr/bin/python3 -u

"""
Summarise the contents of web urls.
NOTE:
  - OPENAI_API_KEY env var required
  - lynx required (brew install lynx)
"""

import os
import signal
import subprocess
import sys
import time

from openai import OpenAI

###
# GLOBALS
###

INSTRUCTIONS = [
    "Summarise the content into 3 most important points, respond in numbered point form",
    "Summarise the content into 6 most important points, respond in numbered point form",
    "Summarise the content into 10 most important points, respond in numbered point form",
]

SUMMARY_INSTRUCTION = "System: Summarise the following text using the instructions provided."
MAX_ARTICLE_LENGTH = 32767 - len(SUMMARY_INSTRUCTION) - 1000

###
# MAIN METHOD
###


def main():
    """Main method"""
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Determine persona
    instructions = instruct_bot()
    print()

    # Create assistant
    assistant = client.beta.assistants.create(model="gpt-4", name="Ooze", instructions=instructions)

    # Create a thread
    thread = client.beta.threads.create()

    # Start
    while True:
        message = input("\033[93m * URL: \033[0m")
        print()

        # Check if finished
        if message.strip().lower() == "done":
            break

        # Grab text
        text = get_page_text(message.strip())

        # Create prompt
        prompt = template_prompt(text)

        # Create a new message for thread
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=prompt)

        # Create a new run
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant.id)

        # Wait for run to execute
        message = wait_for(client, thread.id, run.id)

        # Display message
        print("\n")
        print_as_gpt(message + "\n")

    # Loop finished. Clean up
    client.beta.assistants.delete(assistant.id)
    print_as_gpt("Okay bye.\n")


def instruct_bot():
    """Instruct bot"""
    print("\033[92m * Choose a behaviour for the chatbot:\033[0m")

    # Display options
    for i, instruction in enumerate(INSTRUCTIONS):
        print(f"   {i+1}. {instruction}")
    print()

    # Get choice
    while True:
        try:
            choice = int(input("\033[93m * Your choice: \033[0m"))
            if choice < 1 or choice > len(INSTRUCTIONS):
                raise ValueError
            break
        except ValueError:
            print("\033[91mInvalid choice. Try again.\033[0m")

    # Return instruction
    return INSTRUCTIONS[choice - 1]


def wait_for(client, thread_id, run_id):
    print("\033[92m( thinking ", end="")

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

        if run.status in ["completed", "failed"]:
            # Show cost
            tokens = run.usage.total_tokens

            # Finish thinking bubble
            print(f" [{tokens}] )\033[0m", flush=True)

            # Get only latest message
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            return messages.data[0].content[0].text.value

        else:
            print(".", end="", flush=True)
            time.sleep(1)


# Crawl web url
def get_page_text(url):
    # Call lynx process and capture stdout
    cmd = f"lynx -useragent=\"Mozilla/5.0\" -accept_all_cookies -dump {url}"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    # Truncate if necessary
    if len(out) > MAX_ARTICLE_LENGTH:
        out = out[0:MAX_ARTICLE_LENGTH]

    # Return text
    return out


# Template prompt (TODO: use a proper prompt template)
def template_prompt(text):
    return f"""System: Summarise the following text using the instructions provided.
    Text: {text}
    """


# Print with green
def print_as_gpt(text):
    # Replace newline characters with double-newline characters
    text = text.replace("\r", "\n")

    # Print with green
    print("\033[92m * GPT:\033[0m", text)


# pylint: disable=W0613
def signal_handler(sig, frame):
    """Control signal handler"""
    print(" ")
    sys.exit(0)


# Set up Ctrl-C handler
signal.signal(signal.SIGINT, signal_handler)


###
# MAIN
###

# Invoke main method
if __name__ == "__main__":
    main()
