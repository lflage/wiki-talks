"""
Debugging utilities for parsing Wikipedia talk page threads.

This module provides a function to assist in the debugging of Wikipedia talk page thread parsing.
It allows users to inspect the parsed dictionary, `cur_dict`, interactively and save it to a
JSONL file for later analysis.

Functions:
    thread_parse_debug(cur_dict, target_file="../tests/debug.jsonl"):
        Prompts the user to inspect the parsed thread dictionary and decide whether to save it
        to a file, skip saving, or quit the program.

Usage:
    - The user is prompted to examine each parsed thread's dictionary.
    - 's' saves the dictionary to the specified target file in JSONL format.
    - 'n' skips saving the current dictionary.
    - 'q' quits the program.
"""

import sys
import json
from pprint import pprint


def thread_parse_debug(cur_dict, target_file="../tests/debug.jsonl"):
    """
    Interactively inspects and optionally saves the parsed thread dictionary.

    Args:
        cur_dict (dict): The parsed dictionary representing a talk page thread.
        target_file (str): Path to the JSONL file where selected dictionaries are saved. 
                           Defaults to "../tests/debug.jsonl".

    Prompts:
        's': Saves `cur_dict` to the target file in JSONL format.
        'n': Skips saving the current dictionary.
        'q': Quits the program.
    """
    pprint(cur_dict)
    x = input()
    if x == "s":
        with open(target_file, 'a', encoding='utf8') as f_out:
            json.dump(cur_dict, f_out)
            f_out.write('\n')
    if x == "n":
        return
    if x == "q":
        sys.exit()

def file_inspection(f_path):
    import json
    with open(f_path, 'r', encoding='utf-8') as f:
        for line in f:
            cur_dict = json.loads(line)
            pprint(cur_dict)
            x = input()
            if x == "q":
                sys.exit()

