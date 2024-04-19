#!/usr/bin/python3 -u

"""
Provide descriptions to generate images using DALL-E 3
NOTE: OPENAI_API_KEY env var required
"""

import base64
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
    image_path = check_args()

    # Create client
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Describe image
    description = describe_image(client, image_path)

    # Print description
    print_as_gpt(description)
    print()

    # Prompt for additions to description
    print_as_gpt("Would you like to add anything to the description?")
    print()
    additions = input("\033[93m * You: \033[0m")
    print()

    # Combine description with additions
    if additions.strip() != "":
        description = f"{description}\n{additions}"

    # Recreate image
    create_image(client, description)
    print()

    print_as_gpt("Okay bye.\n")


def describe_image(client, image_path):
    # Encode image
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()

    print(" ( describing image ... ", end="", flush=True)

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
    print()

    # Return result
    return response.choices[0].message.content


def create_image(client, description):
    # Generate image
    print(" ( creating image ... ", end="", flush=True)

    # Open response in browser
    response = client.images.generate(
        model="dall-e-3",
        prompt=description,
        size="1024x1024",
        quality="standard",
        n=1
    )

    print(")", flush=True)
    print()

    # Display image
    webbrowser.open(response.data[0].url)


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
    print("\033[92m * GPT:\033[0m", text, flush=True)


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
