from lxml import etree
import bz2, sys, os, json, re
import wikitextparser as wtp
from wikitextparser import remove_markup

# Future CLI settings
ns_set = {1, 3, 5, 7, 9, 11, 13, 15, 101, 119,711, 829}
out_json = "../dataset/wikitalks.jsonl"
bz2_file = "../dataset/bz2/simplewiki-20240420-pages-meta-current.xml.bz2"

def process_text(text):
    # Do something with the extracted data
    # TODO: process the text removing html, and unnecessary markdown
    return text

def write_to_jsonl(page_dict, path):
    if os.path.exists(path):
        with open(path, 'a') as f_out:
            json.dump(page_dict, f_out)
    else:
        with open(path, "w") as f_out:
            json.dump(page_dict, f_out)

def parse_page(page_dict):
    page = wtp.parse(page)
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
        # if re.match(":", section_txt):
        

    return list
    
def parse_wikipedia_dump(xml_file):
    context = etree.iterparse(xml_file, events=("start", "end"))
    text = ""
    cur_dict = {}

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
                    # TODO

                    # write current dict as json to jsonl output file
                    write_to_jsonl(cur_dict, out_json)
                    sys.exit()
                # Clean the current dict with current parser elements
                cur_dict = {}
                # Free memory by clearing the element
                element.clear()                  

# Replace 'your_wiki_dump.xml' with the path to your Wikipedia XML dump file
with bz2.BZ2File(bz2_file,'rb') as f:
    parse_wikipedia_dump(f)

