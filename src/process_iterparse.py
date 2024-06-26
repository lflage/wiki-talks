import bz2
import sys
import os
import json
import traceback
import wikitextparser as wtp
from wikitextparser import remove_markup
from lxml import etree
import dict_tree

class WikiTalkThreadParser():
    def __init__(self, 
                out_folder="../dataset/jsonl/"):
        self._out_folder = out_folder
        self._ns_set = {1, 3, 5, 7, 9, 11, 13, 15, 101, 119,711, 829}

    # getter setter methods
    def get_ns(self):
        return self.ns_set

    def set_ns(self, new_set:set):
         self._ns_set = new_set
    
    # Path methods
    def get_out_path(self):
        return self._out_path

    def set_out_folder(self,path):
        self._out_folder = path

    def make_out_path(self, in_file):
        file_name = os.path.basename(in_file)
        file_name = os.path.splitext(os.path.splitext(file_name)[0])[0]

        self.out_path = os.path.join(
            self._out_folder,
            file_name + ".jsonl")
        return self.out_path
    
    
    def parse_page(self, page_dict):
        # if there is no text on the page, return empty list
        if page_dict["text"] is None:
            return []
        # Parse page with wikitextparser to return sections
        try:
            page = wtp.parse(page_dict["text"])
        except TypeError:
            # TODO: Properly handle errors, create logs
            print(traceback.format_exc())
            sys.exit()
        threads = []
    
        for i, section in enumerate(page.sections):
            section_txt = ""
            sec_title = section.title
            if sec_title is None and i == 0:
                sec_title = page_dict['title']
    
            sec_text = section.contents
            section_txt += remove_markup(sec_title)
            section_txt += "\n" + remove_markup(sec_text)
            # thread 
            thread = dict_tree.thread_tree(section_txt)
            if thread:
                thread.update({"thread_title": sec_title})
                threads.append(thread)
    
        return threads
        
    def parse_wikipedia_dump(self, file_path:str):

        with bz2.BZ2File(file_path,'rb') as in_file:
            context = etree.iterparse(in_file, events=("start", "end"))
            text = ""
            cur_dict = {}
            ix = 0
            print("started the parser")
            # Create output path
            out_path = self.make_out_path(in_file._fp.name)
            if not os.path.exists(out_path):
                with open(out_path, 'w'):
                     pass
            try:
                for event, element in context:
                    current_tag = element.tag.split("}")[1]
    
                    if event == "start":
                        if current_tag == "ns":
                            try:
                                cur_dict["ns_value"] = int(element.text)
                            except TypeError:
                                cur_dict["ns_value"] = None
    
                        elif current_tag == "title":
                            cur_dict["title"] = ""
                        elif current_tag == "text":
                            text = ""
                    elif event == "end":
                        if current_tag == "title":
                            cur_dict["title"] = element.text
                        elif current_tag == "text":
                            text = element.text
                        elif current_tag == "page":
                            if cur_dict["ns_value"] is not None and cur_dict["ns_value"] in self._ns_set:
                                # Process text/ clean the data
                                cur_dict["text"] = text
                                # assert type(text) == list
                                # create comment thread hierarchy and write to dict
                                cur_dict["threads"] = self.parse_page(cur_dict)
                                # write current dict as json to jsonl output file
                                # TODO: Use wikipedia page id? if there is any
                                cur_dict.update({"id":ix})

                                del cur_dict["text"]
                                # if threads answered write dict
                                if cur_dict["threads"]:
                                    with open(out_path, 'a') as f_out:
                                        json.dump(cur_dict, f_out)
                                        f_out.write('\n')
                                ix +=1
                            # Clean the current dict with current parser elements
                            cur_dict = {}
                            # Free memory by clearing the element
                            element.clear()                  
            except OSError:
                print(file_path)

# Replace 'your_wiki_dump.xml' with the path to your Wikipedia XML dump file
if __name__ == "__main__":
    # Debugging
    import bz2 
    bz2_file = "../dataset/dev/simplewiki-20240420-pages-meta-current.xml.bz2"

    with bz2.BZ2File(bz2_file,'rb') as f:
        print(type(f))
        print(f._fp.name)
        parser = WikiTalkThreadParser()
        parser.parse_wikipedia_dump(f)

