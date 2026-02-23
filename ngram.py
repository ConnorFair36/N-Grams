# Author: Connor Fair
# Class:  CMSC 437 Intro to Natural Language Processing
# Date:   2-22-26

import sys
import re
from collections import Counter
import random

def verify_args(arguments: list[str]) -> tuple:
    if len(arguments) < 3:
        print("Your input must be in the format: ngram.py n m file1.txt file2.txt ...")
        raise ValueError
    n = int(arguments[0])
    m = int(arguments[1])
    files = arguments[2:]
    return n, m, files

def clean_document(document: str) -> str:
    """Cleans the document for n-grams processing."""
    # replace all \n sequences with " "
    document = re.sub(r"\n+", " ", document)
    # expand concatinated words
    document = document.replace("I'm", "I am")
    document = document.replace("'re", " are")
    document = document.replace("let's", "let us")
    document = document.replace("'s", " is")
    document = document.replace("'ve", " have")
    document = document.replace("'d", " did")
    document = document.replace("'ll", " will")
    document = document.replace("n't", " not")
    # replace " ... ... " with " "
    document = document.replace(" ... ... ", " ")
    document = document.replace("... ... ", " ")
    # replace " ..." with <end>
    document = document.replace(" ...", " <end>")
    # replace punctuation at the end of each sentence with <end> tag
    document = re.sub(r"[.!?][^0-9]", " <end> ", document)
    # put the periord for Mr. Ms. and Mrs. back if needed
    document = document.replace("Mr <end>",  "Mr.")
    document = document.replace("Ms <end>",  "Ms.")
    document = document.replace("Mrs <end>", "Mrs.")
    # remove all extra punctuation
    document = re.sub(r"[,'\"()]", "", document)
    # remove capitalization
    document = document.lower()
    # make sure the last characters in the document are an <end> tag
    if document[-6:] != " <end>":
        # remove the period at the end if there is one
        if document[-1] == ".":
            document = document[:-1]
        # make the last word an end tag
        document += " <end>"
    # add <start> to the beginning of each sentence
    document = document.replace(" <end> ", " <end> <start> ")
    # add <start> to the beginning of the document
    document = "<start> " + document
    
    return document

def create_tables(n: int, documents: list[str]) -> list:
    """Creates tables for all values <= n."""
    all_docs = " ".join(documents)
    tables = []
    for i in range(1,n+1):
        tables.append(create_table(i, all_docs))
    return tables

def create_table(n: int,  all_docs: str) -> dict:
    """Creates a table for n based on all_docs."""
    all_words = all_docs.split(" ")
    # a sliding window that concatinates words into n-sequences to be processed
    if n > 1:
        all_words = [" ".join(all_words[i:i+n]) for i in range(len(all_words) - n)]

    n_gram_frequencies = dict(Counter(all_words))
    return n_gram_frequencies

def generate_sentence(tables: list[dict]) -> str:
    """Creates a single sentence."""
    sentence = "<start>"
    next_word = ""
    while next_word != "<end>":
        next_word = get_next_word(tables, sentence)
        # reroll word choice if <start> was chosen
        if next_word == "<start>":
            continue
        sentence += " " + next_word
    # clean up the sentence before printing
    # remove start and end tags
    sentence = sentence[8:-6]
    sentence += "."
    return sentence

def get_next_word(tables: list[dict], sentence: str) -> str:
    """Gets the next word based on the current sentence."""
    # unigrams don't care about context, so just grab a word
    n = len(tables)
    if n == 1:
        uni_table = tables[0]
        return random.choices(list(uni_table.keys()), weights=list(uni_table.values()))[0]
    else:
        # gets the previous n-1 grams fro the sentence
        sentence_words = sentence.split(" ")[-n+1:]
        table = tables[len(sentence_words)]
        # filter down the table keys to just the ones that start with our n-1 grams
        prev_grams = " ".join(sentence_words) + " "
        filtered_keys = [key for key in table.keys() if key.startswith(prev_grams)]
        #print(prev_grams)
        weights = [table[key] for key in filtered_keys]
        # pick the next n words based on the previous n-1 words weighted by their frequencies
        next_sequence = random.choices(filtered_keys, weights=weights)[0]
        # return the last word
        return next_sequence.split(" ")[-1]

def main(arguments: list):
    n, m, files = verify_args(arguments)
    documents = []
    for file in files:
        with open(file=file) as f:
            documents.append(f.read())
    # clean each text file
    documents = [clean_document(doc) for doc in documents]
    tables = create_tables(n, documents)
    # print a sentence for each m
    for s in range(m):
        print(generate_sentence(tables))


if __name__ == "__main__":
    main(sys.argv[1:])
    
