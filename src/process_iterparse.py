from lxml import etree
import bz2, sys, os, json

# Future CLI settings
ns_set = {1, 3, 5, 7, 9, 11, 13, 15, 101, 119,711, 829}
out_json = "../dataset/wikitalks.jsonl"
bz2_file = "../dataset/bz2/simplewiki-20240420-pages-meta-current.xml.bz2"

def process_text(text):
    # Do something with the extracted data
    # TODO: process the text removing html, and unnecessary markdown
   # print("Title:", title)
   # print("Text:", text)
   # print("-----------------------")
    return text

def write_to_jsonl(page_dict, path):
    if os.path.exists(path):
        with open(path, 'a') as f_out:
            json.dump(page_dict, f_out)
    else:
        with open(path, "w") as f_out:
            json.dump(page_dict, f_out)
    
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
                    print("found a Talk namespace")
                    # Process text/ clean the data
                    cur_dict["text"] = process_text(text)
                    # assert type(text) == list
                    print(cur_dict["title"])
                    print("text")
                    print(cur_dict['ns_value'])
                    # create comment thread hierarchy and write to dict
                    # TODO
                    # cur_dict["threads"] = parse_threads(text)
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

