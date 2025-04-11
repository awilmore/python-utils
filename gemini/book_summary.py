#!/usr/bin/env python

import json
import os
import sys

from google import genai
from pydantic import BaseModel, Field


GEMINI_MODEL = "gemini-2.5-pro-exp-03-25"
STANDARD_INSTRUCTION = "System: You are a very intelligent expert in all books. You generate very helpful summaries, listing both key points and interesting facts, about books identified by their author and title. Use the response_schema provided to populate an instance of the BookSummary class with your response.\n"


class BookFact(BaseModel):
    fact: str = Field(description="An interesting fact about the book")
    fact_type: str = Field(description="The type of fact, e.g., 'character', 'plot', 'author', 'country_of_origin' or any other term to summarise the fact.")
    source: str = Field(description="The source of the fact, e.g., 'Wikipedia', 'Author's website' or any other source")


class BookSummary(BaseModel):
    full_title: str = Field(description="The full title of the book")
    author: str = Field(description="The author of the book")
    date_published: str = Field(description="The date the book was published as ISO 8601 formatted string, eg. '2025-03-15T10:30:00Z'")
    summary: str = Field(description="A brief summary of the book")
    key_points: list[str] = Field(description="A list of key points from the book")
    interesting_facts: list[BookFact] = Field(description="A list of interesting facts about the book")


def main():
    """Main method"""
    gemini_api_key = read_api_key()
    client = genai.Client(api_key=gemini_api_key)

    # Ask for details about the book
    title = input(" * Please enter the book's title: ")
    author = input(" * Please enter the book's author: ")

    # Generate book content
    print(" * Fetching book details ... ")
    book = generate_book_summary(client, author, title)

    # Display book content
    print(" * Creating book summary ...")
    print()
    print()

    # Display book title and details
    print(" ****************************************************** ")
    print(f" * Author: {book.author}")
    print(f" * Book Title: {book.full_title}")
    print(f" * Published: {book.date_published}")
    print(" ****************************************************** ")
    print()
    print(f" * Book Summary: {book.summary}")
    print()

    print(" * Key Points:")
    for point in book.key_points:
        print(f"   - {point}")

    print()

    print(" * Interesting Facts:")
    for fact in book.interesting_facts:
        print(f"   - Fact: {fact.fact}")
        print(f"     Fact type: {fact.fact_type}")
        print(f"     Fact source: {fact.source}")
        print()


def generate_book_summary(client, author, title) -> BookSummary:
    # Create instruction to generate book summary
    instruction = STANDARD_INSTRUCTION + "\nAuthor: " + author + "\nTitle: " + title

    try:
        # Send request, get response
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=instruction,
            config={
                'response_mime_type': 'application/json',
                'response_schema': BookSummary,
            },
        )

        # Parse response and return
        return response.parsed

    except genai.errors.ClientError as e:
        self.logger.warning(f"error: gemini responded with exception: {e}")
        output = f"error: gemini responded with exception: {e}"

        if e.code == 429:
            print("error: API requests are being throttled due to heavy usage. Please try again in a few seconds.")

        else:
            print("error: API request failed. Please check the error message and try again.")
            print(f"error: {e}")

        sys.exit(1)


def read_api_key() -> str:
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


# Invoke main method
if __name__ == "__main__":
    main()
