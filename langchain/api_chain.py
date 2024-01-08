#!/usr/bin/python3 -u

from langchain.chat_models import ChatOpenAI
from langchain.chains.api import open_meteo_docs, news_docs
from langchain.chains import APIChain

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
    # setup the chat model
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)

    news_chain = APIChain.from_llm_and_api_docs(
        llm=llm,
        api_docs=news_docs.NEWS_DOCS,
        verbose=False,
        limit_to_domains=["https://newsapi.org"],
        headers={"X-Api-Key": NEWS_API_KEY},
    )

    while True:
        message = input("\033[93m * You: \033[0m")
        print()

        # Check if finished
        if message.strip().lower() == "done":
            break

        # Run the chain
        result = news_chain.run(message)

        # Print result
        print("\n")
        print_as_gpt(result + "\n")

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
