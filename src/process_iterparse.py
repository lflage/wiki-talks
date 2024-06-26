from lxml import etree
import bz2, sys, os, json, re,traceback
import wikitextparser as wtp
from wikitextparser import remove_markup
import dict_tree
import pprint

# Future CLI settings
ns_set = {1, 3, 5, 7, 9, 11, 13, 15, 101, 119,711, 829}
out_json = "../dataset/wikitalks_1.jsonl"
bz2_file = "../dataset/bz2/simplewiki-20240420-pages-meta-current.xml.bz2"

def process_text(text):
    # Do something with the extracted data
    # TODO: process the text removing html, and unnecessary markdown
    return text

def write_to_jsonl(page_dict, path):
    if os.path.exists(path):
        with open(path, 'a') as f_out:
            json.dump(page_dict, f_out)
            f_out.write('\n')
    else:
        with open(path, "w") as f_out:
            json.dump(page_dict, f_out)
            f_out.write('\n')


def parse_page(page_dict):
    # if there is no text on the page, return empty list
    if page_dict["text"] == None:
        return []
    # Parse page with wikitextparser to return sections
    try:
        page = wtp.parse(page_dict["text"])
    except TypeError:
        print(traceback.format_exc())
        pprint.pprint(page_dict)
        sys.exit()
    threads = []

    for i, section in enumerate(page.sections):
        section_txt = ""
        sec_title = section.title
        if sec_title == None and i == 0:
            sec_title = page_dict['title']

        sec_text = section.contents
        section_txt += remove_markup(sec_title)
        section_txt += "\n" + remove_markup(sec_text)
        # thread 
        thread = dict_tree.thread_tree(section_txt)
        if thread:
            thread.update({"thread_title": sec_title})
            #pprint.pprint(thread)
            threads.append(thread)

    return threads
    
def parse_wikipedia_dump(xml_file):
    context = etree.iterparse(xml_file, events=("start", "end"))
    text = ""
    cur_dict = {}
    ix = 0
    print("started the parser")

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
                if cur_dict["ns_value"] is not None and cur_dict["ns_value"] in ns_set:
                    # Process text/ clean the data
                    cur_dict["text"] = text
                    # assert type(text) == list
                    # create comment thread hierarchy and write to dict
                    cur_dict["threads"] = parse_page(cur_dict)

                    # write current dict as json to jsonl output file
                    # TODO: Use wikipedia page id? if there is any
                    cur_dict.update({"id":ix})
                    if cur_dict["threads"]:
                        write_to_jsonl(cur_dict, out_json)
                    ix +=1
                # Clean the current dict with current parser elements
                cur_dict = {}
                # Free memory by clearing the element
                element.clear()                  

# Replace 'your_wiki_dump.xml' with the path to your Wikipedia XML dump file
if __name__ == "__main__":
    with bz2.BZ2File(bz2_file,'rb') as f:
        parse_wikipedia_dump(f)

