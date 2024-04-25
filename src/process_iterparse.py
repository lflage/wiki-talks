from lxml import etree
import bz2, sys, os, json

ns_set = {1,3,5,7,9}
out_json = "./wikitalks.jsonl"
# TODO: add dict to save as json
cur_dict = {}

def process_text(text):
    # Do something with the extracted data
    # TODO: process the text removing html, and unnecessary markdown
    print("Title:", title)
    print("Text:", text)
    print("-----------------------")
    return text

def write_to_jsonl(page_dict, path):
    if os.path.exists(path):
        with open(path, 'a') as f_out:
            json.dump(page_dict, path)
    else:
        with open(path, "w") as f_out:
            json.dump(page_dict, path)


def parse_wikipedia_dump(xml_file):
    context = etree.iterparse(xml_file, events=("start", "end"))
    title = ""
    text = ""
    ns_value = None

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
                cur_dict["title"] += element.text
            elif current_tag == "text":
                text += element.text
            elif current_tag == "page":
                print("found a page")
                if ns_value is not None and ns_value in ns_set:
                    # Process text/ clean the data
                    text = process_text(text)
                    # create comment thread hierarchy and write to dict
                    # TODO
                    cur_dict["threads"] = parse_threads(text)
                    # write current dict as json to jsonl output file
                    write_to_jsonl(cur_dict, path)
                # Clean the current dict with current parser elements
                cur_dict = {}
                # Free memory by clearing the element
                element.clear()                  

# Replace 'your_wiki_dump.xml' with the path to your Wikipedia XML dump file
with bz2.BZ2File('../dataset/simplewiki-20240401-pages-meta-current.xml.bz2','rb') as f:
    parse_wikipedia_dump(f)

