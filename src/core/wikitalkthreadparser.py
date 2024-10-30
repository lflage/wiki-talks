"""
WikiTalkThreadParser module.

This module provides a class, `WikiTalkThreadParser`, to parse Wikipedia talk page 
dump files in .bz2 format and extract threaded discussion data. The extracted data 
is saved in JSONL format for each language in a specified output directory.

Classes:
    - WikiTalkThreadParser: Parses Wikipedia talk page dumps, extracts threaded 
      discussions, and outputs them in JSONL format.

Attributes:
    parse_logger (Logger): Logger instance for logging parsing information and errors.
"""

import bz2
import sys
import os
import json
from lxml import etree
from ..utils.debbuger import thread_parse_debug
from ..utils.log_utils import setup_logger
from ..utils.date_signatures import date_sign_dict
from .pageparser import PageParser

# Configure parse_logger for logging parse activities and exceptions
parse_logger = setup_logger(__file__)

class WikiTalkThreadParser:
    """
    Parses Wikipedia talk page dumps, extracting threaded discussions and saving them as JSONL.

    Attributes:
        out_folder (str): The output folder path for saving JSONL files.
        ns_set (set): Namespace set to filter which namespaces to parse.
        debug (bool): Debug flag; when True, saves the original text in the output.

    Methods:
        get_ns(): Returns the set of namespaces currently set.
        set_ns(new_set): Sets a new set of namespaces to parse.
        get_out_path(): Returns the current output path.
        set_out_folder(path): Sets the output folder path.
        make_out_path(in_file): Creates and returns the output file path based on input file name.
        parse_page(page_dict): Parses an individual page's text into threaded discussions.
        parse_wikipedia_dump(file_path): Main function to parse the entire Wikipedia dump file.
    """

    def __init__(self, out_folder="../dataset/jsonl/"):
        """Initialize with output folder and namespace set."""
        self._out_folder = out_folder
        self._ns_set = {1, 3, 5, 7, 9, 11, 13, 15, 101, 119, 711, 829}
        self.debug = False  # Debug flag to return original text if needed

    # Getter and setter methods for namespace set
    def get_ns(self):
        """Return the current set of namespaces."""
        return self._ns_set

    def set_ns(self, new_set: set):
        """Set a new namespace set to define which namespaces to parse."""
        self._ns_set = new_set

    # Output path management methods
    def get_out_path(self):
        """Return the current output path."""
        return self._out_folder

    def set_out_folder(self, path):
        """Set the output folder path."""
        self._out_folder = path

    def make_out_path(self, in_file):
        """
        Create the output file path based on the input file name.

        Args:
            in_file (str): Path of the input .bz2 file.

        Returns:
            str: The generated output path for the JSONL file.
        """
        file_name = os.path.basename(in_file)
        file_name = os.path.splitext(os.path.splitext(file_name)[0])[0]
        lang = file_name[:2]  # Infer language from filename prefix

        self.out_path = os.path.join(
            self._out_folder,
            lang,
            file_name + ".jsonl"
        )
        return self.out_path

    def parse_page(self, page_dict):
        """
        Parse an individual page's text into threads.

        Args:
            page_dict (dict): Dictionary with page data including text content.

        Returns:
            list: List of parsed threads from the page.
        """
        if page_dict["text"] is None:
            return []  # Return empty if no text is present

        # Parse page using PageParser based on language's date format
        parser = PageParser(page_dict["text"], self.lang)
        if self.lang in date_sign_dict.keys():
            threads = parser.wtp_parse(page_dict['text'])
        else:
            try:
                threads = parser.full_parse()
            except TypeError:
                parse_logger.error("Type error during parsing", exc_info=True)
                sys.exit()
        return threads

    def parse_wikipedia_dump(self, file_path: str):
        """
        Parse the entire Wikipedia dump file, extracting discussions and saving to JSONL.

        Args:
            file_path (str): Path to the Wikipedia dump .bz2 file.
        """
        with bz2.BZ2File(file_path, 'rb') as in_file:
            context = etree.iterparse(in_file, events=("start", "end"))
            text = ""
            cur_dict = {}
            ix = 0

            print("Started parsing")
            out_path = self.make_out_path(in_file._fp.name)
            if not os.path.exists(out_path):
                with open(out_path, 'w', encoding='utf-8'):
                    pass  # Create empty file if not exists
            else:
                print(f"Output file already exists: {out_path}")
                return

            try:
                for event, element in context:
                    current_tag = element.tag.split("}")[1]

                    # Capture language, namespace, title, and base URL
                    if event == "start":
                        if current_tag == "mediawiki":
                            self.lang = element.get("{http://www.w3.org/XML/1998/namespace}lang")
                        elif current_tag == "ns":
                            cur_dict["ns_value"] = int(element.text) if element.text else None
                        elif current_tag == "title":
                            cur_dict["title"] = ""
                        elif current_tag == "text":
                            text = ""
                        elif current_tag == "base":
                            base_url = ""
                    elif event == "end":
                        if current_tag == "title":
                            cur_dict["title"] = element.text
                        elif current_tag == "text":
                            text = element.text
                        elif current_tag == "base":
                            base_url = element.text
                        elif current_tag == "page":
                            if cur_dict["ns_value"] in self._ns_set:
                                cur_dict["text"] = text
                                cur_dict["threads"] = self.parse_page(cur_dict)
                                cur_dict.update({"id": ix,
                                "url": os.path.join(os.path.split(base_url)[0], cur_dict["title"])})

                                # Output JSONL data with or without debug
                                if self.debug:
                                    thread_parse_debug(cur_dict)
                                else:
                                    del cur_dict["text"]
                                    if cur_dict["threads"]:
                                        with open(out_path, 'a', encoding='utf-8') as f_out:
                                            json.dump(cur_dict, f_out)
                                            f_out.write('\n')
                                ix += 1
                            cur_dict = {}  # Reset dictionary for next page
                            element.clear()  # Free memory by clearing element

            except Exception as e:
                parse_logger.exception("Parsing error in file %s: %s",file_path, e)

if __name__ == "__main__":
    # Debugging example
    parser = WikiTalkThreadParser()
    parser.set_out_folder("./testing_folder/")
    parser.make_out_path("../dataset/raw/enwiki-20240601-pages-meta-current.xml.bz2")
    print(parser.out_path)
    # Uncomment to debug parsing
    # parser.DEBUG = True
    # parser.set_out_folder('../dataset/v1_0_0')
    # parser.parse_wikipedia_dump(bz2_file)
