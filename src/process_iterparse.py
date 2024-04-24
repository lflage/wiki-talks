from lxml import etree
import bz2
import sys

ns_set = {1,3,5,7,9}
# TODO: add dict to save as json
cur_dict = {}

def process_text(title, text):
    # Do something with the extracted data
    # TODO: process the text removing html, and unnecessary markdown
    print("Title:", title)
    print("Text:", text)
    print("-----------------------")

def write_to_jsonl(page_dict, path):



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
                    ns_value = int(element.text)
                except TypeError:
                    ns_value = None

            elif current_tag == "title":
                title = ""
            elif current_tag == "text":
                text = ""
        elif event == "end":
            if current_tag == "title":
                title = element.text
            elif current_tag == "text":
                text = element.text
            elif current_tag == "page":
                print("found a page")
                if ns_value is not None and ns_value in ns_set:
                    process_text(text)

                    write_to_jsonl()
                title = ""
                text = ""
                ns_value = None
                element.clear()  # Free memory by clearing the element
                

# Replace 'your_wiki_dump.xml' with the path to your Wikipedia XML dump file
with bz2.BZ2File('../dataset/simplewiki-20240401-pages-meta-current.xml.bz2','rb') as f:
    parse_wikipedia_dump(f)

