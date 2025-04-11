#!/usr/bin/env python3

"""
Provide descriptions to generate images using Imagen 3
NOTE: GEMINI_API_KEY env var required
"""

import os
import signal
import sys

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO


###
# MAIN METHOD
###

def main():
    """Main method"""
    gemini_api_key = read_api_key()
    client = genai.Client(api_key=gemini_api_key)

    print()

    # Start
    while True:
        message = input("\033[93m * Describe image: \033[0m")
        print()

        # Check if finished
        if message.strip().lower() == "done":
            break

        # Generate image
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=message,
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )

        # Display image
        for generated_image in response.generated_images:
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            image.show()

    # Loop finished. Clean up
    print("Okay bye.")


def read_api_key():
    """Read API key from environment variable"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        print("error: env var not found: %s" % "GEMINI_API_KEY")
        sys.exit(1)

    return gemini_api_key


# pylint: disable=W0613
def signal_handler(sig, frame):
    """Control signal handler"""
    print(" ")
    sys.exit(0)


# Set up Ctrl-C handler
signal.signal(signal.SIGINT, signal_handler)


# Invoke main method
if __name__ == "__main__":
    main()
