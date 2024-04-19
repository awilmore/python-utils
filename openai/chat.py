#!/usr/bin/python3 -u

"""
Start conversation with ChatGTP
NOTE: OPENAI_API_KEY env var required
"""

import os
import sys
import signal
import time

from openai import OpenAI

###
# GLOBALS
###

INSTRUCTIONS = [
    "Be as helpful as possible",
    "You are an extremely chilled out surfer guy. You start each response with the word 'yo' and finish with the word 'dude'",
    "Respond to all questions using the manner in which Yoda speaks",
    "Respond to all questions as though writing a Shakespearean play",
    "Respond to all questions with useless, unhelpful and incorrect answers. Be as creative as possible",
    "Respond to all questions with a creative answer that ultimately results in the number '42'",
    "Respond to all questions starting with the phrase 'I am a cybernetic organism', then answer the question like Arnold Schwarzenegger would",
    "When you respond, talk like an Aussie bogan from north queensland",
    "You must only reply with two words: use 'cells' when it is an objective question and 'interlinked' when it is a subjective question",
]

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
        message = input("\033[93m * You: \033[0m")
        print()

        # Check if finished
        if message.strip().lower() == "done":
            break

        # Create a new message for thread
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=message)

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

            # Check for error message
            if run.last_error:
                return run.last_error.message

            # Get only latest message
            messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            return messages.data[0].content[0].text.value

        else:
            print(".", end="", flush=True)
            time.sleep(1)


# Print with green
def print_as_gpt(text):
    """Print with green"""
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
