"""
Module for parsing threaded discussions from WikiText format.

This module contains functions to parse structured text with indentation and
date signatures, organizing content hierarchically for threads with or without
titles. The parsed data is structured in a dictionary format that groups
replies based on indentation depth.
"""

import re
from wikitextparser import remove_markup
from ..utils.log_utils import setup_logger
from ..utils.date_signatures import date_sign_dict

dict_tree_logger = setup_logger(__file__)


def check_depth(text, base=1):
    """
    Determine the depth of a comment based on indentation (using ':' characters).

    Parameters:
    - text (str): The text to check for indentation.
    - base (int): The base depth to use if no indentation is found (default is 1).

    Returns:
    - int: Calculated depth based on leading ':' characters.
    """
    match = re.match(":+", text)
    if match:
        start, end = match.span()
        depth = end - start
        return depth + base
    return base


def thread_tree(text, lang):
    """
    Parse a thread with date-signature recognition to build a tree of comments and replies.

    Parameters:
    - text (str): The thread text to parse.
    - lang (str): Language code used to locate the corresponding date signature pattern.

    Returns:
    - dict: Parsed thread data with 'message' as root text and 'replies' as a list of replies.
    """
    pattern = date_sign_dict[lang]
    date_signature = re.compile(pattern)
    text = re.sub("\n+", "\n", text).strip()

    # Identify main thread text and any replies
    search = re.search(date_signature, text)
    try:
        thread_text = search.string[:search.end()]
        replies_text = search.string[search.end():]
    except AttributeError:
        return None

    thread_text = remove_markup(thread_text)
    thread = {"message": thread_text, "replies": []}

    # If there are no replies, return the main message only
    if not replies_text.strip():
        return thread

    stack = [thread]
    for ix, split in enumerate(replies_text.split("\n:")[1:], start=1):
        split = split.strip()
        depth = check_depth(split)

        # Attempt to parse reply text
        try:
            search_result = re.search(date_signature, split)
            text = search_result.string[:search_result.end()][depth - 1:]
        except AttributeError as e:
            dict_tree_logger.debug(e)
            return {}

        text = remove_markup(text)
        reply = {"text": text, "replies": []}

        # Organize replies based on depth relative to stack
        if depth > len(stack):
            stack[-1]["replies"].append(reply)
        elif depth == len(stack):
            stack[-1]["replies"].append(reply)
        elif depth < len(stack):
            dif = len(stack) - depth
            stack = stack[:-dif]
            stack[-1]["replies"].append(reply)

        stack.append(reply)
    return thread


def thread_no_title(text, lang):
    """
    Parse threads without a title, using indentation as the only structure for replies.

    Parameters:
    - text (str): The content of the thread to parse.
    - lang (str): Language code used to locate the date signature pattern.

    Returns:
    - dict: Parsed thread data structured with 'message' as root text and 'replies' as list of replies.
    """
    comment_indent = r"\n:"
    text = re.sub("\n+", "\n", text).strip()
    thread = {'message': "", 'replies': []}

    # Identify the first comment
    first_comment = re.search(r"\n:", text)
    if not first_comment:
        thread["message"] = text
        return thread

    thread_text = text[:first_comment.start()]
    thread_comments = text[first_comment.end():]
    thread_text = remove_markup(thread_text)
    thread["message"] = thread_text

    stack = [thread]

    # Iterate over comments split by indentation
    for split in re.split(comment_indent, thread_comments):
        split = split.strip()
        depth = check_depth(split)

        search_result = re.match(r":", split)
        if search_result:
            # Adjust text based on depth
            text = search_result.string[search_result.start():]
        else:
            text = split

        text = remove_markup(text)
        reply = {"text": text, "replies": []}

        # Append replies at the correct depth level
        if depth > len(stack):
            stack[-1]["replies"].append(reply)
        elif depth == len(stack):
            stack[-1]["replies"].append(reply)
        elif depth < len(stack):
            dif = len(stack) - depth
            stack = stack[:-dif]
            stack[-1]["replies"].append(reply)

        stack.append(reply)

    return thread


if __name__ == "__main__":
    pass
