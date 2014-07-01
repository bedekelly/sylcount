#!/usr/bin/python3
"""
Usage:
    sylcount -w word
    sylcount -f filename
"""

import re
import sys
import os
import urllib
from sys import argv
from urllib.request import urlopen

NUM_WORDS = None

class WordNotExist(Exception):
    pass

class BadInput(Exception):
    pass


class colors:
    GREEN = '\033[32m'
    RED = '\033[31m'
    REVERT = '\033[0m'
    BLUE = '\033[34m'


def memoize(func):
    memo = {}
    def helper(x):
        if x not in memo:            
            memo[x] = func(x)
        return memo[x]
    return helper


@memoize  # Not actually used at the moment; program already implements some 
          # kind of memoization with set().
def get_syllables(given_word):
    # addr = "http://dictionary.reference.com/browse/{}".format(given_word)
    # # Scrape webpage for given word
    # webpage = urlopen(addr).read().decode(sys.stdout.encoding)
    # expr = re.compile('e=.*</h')  # Matches word with syllable markings
    # matches = re.findall(expr, webpage)
    # if matches:
    #   word = matches[0]

    #   # Trim the start and end, remove the 'raw' word that comes afterwards.
    #   word = word[3:-(3+len(given_word))]
    #   # Get rid of extra symbols.
    #   word = word.replace("\">", "")

    #   # Count syllable separators and add 1.
    #   syllables = word.count("·") + 1
    #   return syllables

    # else:
    #   raise WordNotExist

    addr = "http://www.syllablecount.com/how_many_syllables/" + given_word
    try:
        webpage = urlopen(addr).read().decode(sys.stdout.encoding)
    except urllib.error.HTTPError:
        raise BadInput("Use the -f option for full sentence analysis.")
    expr = re.compile('''000'>.*?<''')
    matches = re.findall(expr, webpage)
    if matches:
        match = matches[0]
        number_syllables = int(match[5:-1])
        return number_syllables
    else:
        raise WordNotExist


def print_info(wordlist):
    info, total, mode, notfound = get_multiple(wordlist)
    list_by_syllables = sorted(info.items(),
                               key=lambda word: word[1]["syllables"])
    most_syllables = list_by_syllables[-1]

    print()
    if supports_colors:
        num_not_found = len(notfound)
        print("{}{}{} words not recognised.".format(
            colors.RED if num_not_found else colors.GREEN,
            num_not_found,
            colors.REVERT
            ))

        print("\nWord with most syllables: {}{}{} ({}{}{} syllable(s))".format(
            colors.BLUE,
            most_syllables[0],
            colors.REVERT,

            colors.BLUE,
            most_syllables[1]["syllables"],
            colors.REVERT
            ))

        print("\nWord with most occurances: {}{}{} ({}{}{} instance(s))".format(
            colors.BLUE,
            mode[0],
            colors.REVERT,

            colors.BLUE,
            mode[1]['occurances'],
            colors.REVERT
            ))

        print("Total number of syllables: {}{}{}".format(
            colors.BLUE,
            total,
            colors.REVERT
            ))
    else:
        print("{} words not recognised.".format(len(notfound)))


def get_multiple(wordlist):
    info = {}
    notfound = []
    for word in set(wordlist):
        print("\rAnalysing word: {}".format(word) + " "*20, end='')
        sys.stdout.flush()
        try:
            info[word] = {
                "syllables": get_syllables(word),
                "occurances": wordlist.count(word)
                }
        except WordNotExist:
            print("...Not found.")
            notfound.append(word)

    total = 0
    for word in info.values():
        # print(word)
        total += word["syllables"] * word["occurances"]
    # print(total)

    sorted_by_occurances = sorted(info.items(),
                                  key=lambda key: key[1]['occurances'])
    mode = sorted_by_occurances[0]
    return info, total, mode, notfound


def single_info(word):
    no_syllables = get_syllables(word)
    info_string = "'{}' has {}{}{} syllable(s).".format(
        word.title(),
        colors.RED if supports_colors else '',
        no_syllables,
        colors.REVERT if supports_colors else '')
    return info_string


def main():
    if len(argv) == 3:
        if argv[1] == "-f":
            # If filename exists:
            if os.path.exists(os.path.join(os.path.expanduser("."), argv[2])):
                with open(argv[2]) as wordlist_file:
                    # Get list of words from file
                    raw_words = wordlist_file.read().split()
                    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
                    # Strip all punctuation off words
                    words = [(''.join(ch for ch in word if ch not in punc)
                                .lower().strip())
                                for word in raw_words]

                print_info(words[:NUM_WORDS])
            else:
                print("File does not exist.")
        elif argv[1] == "-w":
            # Print information about a single word
            print(single_info(argv[2]))
        else:
            print(__doc__)
    else:
        print(__doc__)


if __name__ == "__main__":
    # Posix, unix, linux, OSX
    supports_colors = 'x' in sys.platform
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting now.")