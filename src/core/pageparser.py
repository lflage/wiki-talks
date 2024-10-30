"""
Module for parsing Wikipedia talk page discussions.

This module provides the `PageParser` class, which parses Wikipedia talk page discussions into
structured thread data. It identifies headers and threads, applies language-specific date
signatures, and creates a hierarchical thread structure.

Classes:
    PageParser: Parses Wikipedia talk page text based on headers, separators, and date signatures.

Usage:
    - Initialize `PageParser` with the page content and language.
    - Use `full_parse()` to obtain a list of parsed discussion threads.
"""

import re
from pprint import pprint
import wikitextparser as wtp
from .dict_tree import thread_tree, thread_no_title
from ..utils.date_signatures import date_sign_dict



class PageParser:
    """
    Parses a Wikipedia talk page into threads based on headers, separators, and date signatures.
    """
    # Regular expressions for identifying headers and section rulers
    HEADER = r"(={2,6})(.*?)(\1)"
    RULER = r"\n-{4,}"

    def __init__(self, to_parse, lang):
        """
        Initializes the parser with page content and language.

        Args:
            to_parse (str): The Wikipedia talk page text to parse.
            lang (str): The language code of the page, which determines parsing behavior.
        
        att:
            to_parse (str): The Wikipedia talk page text to parse.
            main_parse_function (function): Function for parsing threads, chosen based on language.
        """
        self.to_parse = to_parse
        self.lang = lang

        # Use date signature to mark end of comment if available for the language
        if self.lang in date_sign_dict:
            self.main_parse_function = thread_tree
        else:
            self.main_parse_function = thread_no_title

    def full_parse(self):
        """
        Parses the entire Wikipedia talk page, separating threads and processing headers.

        Returns:
            list: A list of parsed threads from the page.
        """
        threads_list = []

        # Check if page contains a header
        match = re.search(self.HEADER, self.to_parse)

        # Check if there is text before a header
        if match:
            trailing_text = match.string[:match.start()]
            if trailing_text:
                word_character_trailing_text = re.sub(r'\W+', '', trailing_text)

                # If there is text before a header, check for alternate uses of separators like ----
                if len(word_character_trailing_text) > 10:
                    if re.search(self.RULER, trailing_text):
                        # Gets all threads before the first header
                        for thread_text in re.split(self.RULER, trailing_text):
                            cur_thread = thread_no_title(thread_text, self.lang)
                            threads_list.append(cur_thread)

                        # Parses from the first header forward
                        threads_list.extend(self.wtp_parse(match.string[match.start():]))
                    else:
                        # Parses entire text if no section ruler is present
                        threads_list.extend(self.wtp_parse(self.to_parse))
            else:
                # Parse normally if no trailing text is found before headers
                intermediate_list = self.wtp_parse(self.to_parse)
                threads_list.extend(intermediate_list)

        return threads_list

    def wtp_parse(self, text):
        """
        Parses sections of Wikipedia talk page using `wikitextparser` library.

        Args:
            text (str): Section of text to parse for threads.

        Returns:
            list: Parsed threads from each section.
        """
        threads_list = []
        page = wtp.parse(text)
        for section in page.sections:
            section_txt = ""
            sec_title = section.title
            sec_text = section.contents

            section_txt += "\n" + wtp.remove_markup(sec_text)

            thread = self.main_parse_function(section_txt, self.lang)
            if thread:
                thread.update({"thread_title": sec_title})
                threads_list.append(thread)
        return threads_list


if __name__ == "__main__":
    import json
    # For debugging: loads example JSONL file and parses its content
    with open("../tests/debug.jsonl", 'r', encoding='utf-8') as f:
        for line in f.readlines():
            content = json.loads(line)
            try:
                parser = PageParser(content['text'], "en")
            except KeyError:
                continue
            threads = parser.full_parse()
            pprint(threads)
            x = input()
