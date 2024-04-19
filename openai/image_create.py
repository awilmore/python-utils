#!/usr/bin/python3 -u

"""
Provide descriptions to generate images using DALL-E 3
NOTE: OPENAI_API_KEY env var required
"""

import os
import signal
import sys
import webbrowser

from openai import OpenAI


###
# MAIN METHOD
###


def main():
    """Main method"""
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    print()

    # Start
    while True:
        message = input("\033[93m * Describe image: \033[0m")
        print()

        # Check if finished
        if message.strip().lower() == "done":
            break

        # Generate image
        response = client.images.generate(
            model="dall-e-3",
            prompt=message.strip(),
            size="1024x1024",
            quality="standard",
            n=1
        )

        # Display image
        webbrowser.open(response.data[0].url)

    # Loop finished. Clean up
    print_as_gpt("Okay bye.\n")


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
