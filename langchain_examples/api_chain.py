#!/usr/bin/python3 -u

from langchain.chains.openai_functions.openapi import get_openapi_chain
from langchain_openai import ChatOpenAI

import json
import os
import signal
import sys


###
# GLOBALS
###

OPENAI_MODEL = "gpt-4"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWSAPI_ORG_KEY")


###
# MAIN METHOD
###

def main():
    # Setup chat model
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)

    chain = get_openapi_chain(
        spec="https://www.klarna.com/us/shopping/public/openai/v0/api-docs/",
        llm=llm
    )

    while True:
        message = input("\033[93m * You: \033[0m")
        print()

        # Check if finished
        if message.strip().lower() == "done":
            break

        # Run the chain
        r = chain(message)
        response = json.dumps(r["response"], indent=4)

        # Print result
        print("\n")
        print_as_gpt(response + "\n")

    # Clean up
    print_as_gpt("Okay bye.\n")


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
