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
import random
from lxml import etree
from src.config import SAMPLES_DIR
from ..utils.debbuger import thread_parse_debug, file_inspection
from ..utils.log_utils import setup_logger
from ..utils.date_signatures import date_sign_dict
from .pageparser import PageParser
from filter import thread_max_depth

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
        self._sample_mode = True
        self._sample_size = 100
        self._reservoir = []
        self._seen = 0
        self._checkpoint_file = os.path.join(out_folder, ".parsing_checkpoint.json")
        self._parsed_files = self._load_checkpoint()
        self._files_parsed_count = 0

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

    
    def enable_sampling(self, sample_size: int = 100):
        """Enable reservoir sampling mode."""
        self._sample_mode = True
        self._sample_size = sample_size
        self._reservoir = []
        self._seen = 0

    def _reservoir_sample(self, item: dict):
        """
        Update reservoir with a new item using Knuth's Algorithm R.
        Guarantees a uniform random sample without knowing total count.
        """
        self._seen += 1
        if len(self._reservoir) < self._sample_size:
            self._reservoir.append(item)
        else:
            # Randomly replace an element with decreasing probability
            j = random.randint(0, self._seen - 1)
            if j < self._sample_size:
                self._reservoir[j] = item

    def _load_checkpoint(self) -> dict:
        """Load previously parsed files from checkpoint."""
        if os.path.exists(self._checkpoint_file):
            try:
                with open(self._checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_checkpoint(self):
        """Save checkpoint of parsed files."""
        os.makedirs(os.path.dirname(self._checkpoint_file), exist_ok=True)
        with open(self._checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self._parsed_files, f, indent=2)

    def _record_parsed_file(self, file_path: str):
        """Record a successfully parsed file in checkpoint."""
        self._parsed_files[file_path] = {
            "timestamp": str(os.path.getmtime(file_path)),
            "parsed_successfully": True
        }
        self._files_parsed_count += 1
        self._save_checkpoint()

    def get_parsed_files_count(self) -> int:
        """Return the total number of successfully parsed files from checkpoint."""
        return len(self._parsed_files)

    def save_sample(self, out_path: str):
        """Write the collected reservoir sample to a JSONL file."""
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            for item in self._reservoir:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        print(f"Saved {len(self._reservoir)} samples to {out_path}")

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
        self.lang = file_name[:2]  # Infer language from filename prefix

        self.out_path = os.path.join(
            self._out_folder,
            self.lang,
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
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            with open(out_path, 'a', encoding='utf-8') as f_out:
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
                                    cur_dict.update({
                                        "id": ix,
                                        "url": os.path.join(os.path.split(base_url)[0], cur_dict["title"])
                                    })

                                    
                                    # # Remove threads with depth less than 2
                                    # # considers them to not have discussions
                                    # cur_dict["threads"] = [
                                    #                     thread for thread in cur_dict["threads"]
                                    #                     if thread_max_depth(thread) > 2
                                    #                     ]

                                    if self._sample_mode:
                                        # Keep text in sample for manual inspection
                                        if cur_dict["threads"]:
                                            self._reservoir_sample(dict(cur_dict))
                                    # Output JSONL data with or without debug
                                    else:
                                        if self.debug:
                                            thread_parse_debug(cur_dict)
                                        else:
                                            del cur_dict["text"]
                                            if cur_dict["threads"]:
                                                json.dump(cur_dict, f_out)
                                                f_out.write('\n')
                                    ix += 1
                                cur_dict = {}  # Reset dictionary for next page
                                element.clear()  # Free memory by clearing element

                except Exception as e:
                    parse_logger.exception("Parsing error in file %s: %s",file_path, e)
                else:
                    # Record successful parse only if no exception occurred
                    self._record_parsed_file(file_path)
                    self.save_sample(f"{SAMPLES_DIR}/samples{self.lang}")
                
                parse_logger.info(f"SUCCESS: parsed {file_path} in {self.out_path}")


def main():
    import argparse
    from tqdm import tqdm
    from .wikidumpdownloader import WikiDumpDownloader

    parser = argparse.ArgumentParser(description="Generate dataset from Wikipedia talk page dumps.")
    parser.add_argument('--raw_path', type=str, default="./data/raw", help='Path to stored downloaded .bz2 files.')
    parser.add_argument('--output', type=str, default="data/datasets", help='Path to store output JSONL files.')
    parser.add_argument('--langs', type=str, nargs='*', help='List of language codes to process (e.g., en, de). If empty, processes all languages.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to inspect parsed threads interactively. Needs final output file')
    args = parser.parse_args()

    bz2_file_path = args.raw_path
    # jsonl_file_paths = args.output
    # langs = args.langs if args.langs else []

    
    parser = WikiTalkThreadParser()
    parser.parse_wikipedia_dump(bz2_file_path)

if __name__ == "__main__":
    main()
    # Debugging example
#    bz2_file = "/home/lucasfl/Documents/repos/wiki-talks/wiki-talks/data/raw/ptwiki-20250920-pages-meta-current.xml.bz2"
#    parser.set_out_folder("./data/test_folder")
#    parser.make_out_path(bz2_file)
#    print(parser.out_path)
#    # Uncomment to debug parsing
#    parser.debug = True
#    if parser.debug:
#        file_inspection(parser.out_path)
#    parser.parse_wikipedia_dump(bz2_file)