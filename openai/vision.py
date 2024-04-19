#!/usr/bin/python3 -u

"""
Provide descriptions to generate images using DALL-E 3
NOTE: OPENAI_API_KEY env var required
"""

import base64
import os
import signal
import subprocess
import sys
import time

from openai import OpenAI


###
# MAIN METHOD
###


def main():
    """Main method"""
    image_path = check_args()

    # Encode image
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()

    # Create client
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    print(" ( thinking ... ", end="")

    # Describe image
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image? Be as detailed as possible",
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    }
                ]
            }
        ]
    )

    print(")", flush=True)

    # Fetch result
    description = response.choices[0].message.content

    # Display result
    print()
    print_as_gpt(description)
    print()


def check_args():
    if len(sys.argv) != 2:
        usage()

    return sys.argv[1]


def usage():
    script_name = sys.argv[0]
    print("usage: %s path_to_image" % script_name)
    sys.exit()


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
