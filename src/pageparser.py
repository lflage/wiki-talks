import dict_tree
import re
import json
import wikitextparser as wtp
from pprint import pprint

header = r"(={2,6})(.*?)(\1)"
ruler = r"\n-{4,}"

date_sign_dict = json.load(open("../utils/date_signatures.json"))

class PageParser():
    def __init__(self, to_parse, lang):
        self.attempts = 0
        self.to_parse = to_parse
        self.lang = lang

        # If there is a date signature regex, use the date signature to mark end of comment
        # else use the colon marking the next comment to mark end of initial comment
        if self.lang in date_sign_dict.keys():
            self.main_parse_function = dict_tree.thread_tree
        else:
            self.main_parse_function = dict_tree.thread_no_title
        

    def full_parse(self):
        threads_list = []

        # check if page contains a header
        match = re.search(header, self.to_parse)

        # check if there is text before a header
        if match:
            trailing_text = match.string[:match.start()]
            if trailing_text:
                word_character_trailing_text = re.sub(r'\W+', '', trailing_text)

                # if there is text before a header, check for alternate uses of separators
                # like ------
                if len(word_character_trailing_text) > 10:
                    if re.search(ruler, trailing_text):
                        for thread_text in re.split(ruler, trailing_text):
                            # print(thread_text)
                            # x = input("press to continue")
                            cur_thread = dict_tree.thread_no_title(thread_text,self.lang)
                            threads_list.append(cur_thread)
                        threads_list.extend(self.wtp_parse(match.string[match.start():]))
                    else:
                        threads_list.append(self.wtp_parse(self.to_parse))

            else:
                intermediate_list = self.wtp_parse(self.to_parse)
                threads_list.extend(intermediate_list)

        return threads_list
    
    def wtp_parse(self, text):
        threads_list = []
        page = wtp.parse(text)
        for i, section in enumerate(page.sections):
            section_txt = ""
            sec_title = section.title
            sec_text = section.contents
            # section_txt += wtp.remove_markup(sec_title)
            section_txt += "\n" + wtp.remove_markup(sec_text)
            # thread 
            thread = self.main_parse_function(section_txt, self.lang)
            if thread:
                thread.update({"thread_title": sec_title})
                threads_list.append(thread)
        return threads_list

    

if __name__=="__main__":
    import json
    with open("../tests/debug.jsonl",'r') as f:
        for line in f.readlines():
            content = json.loads(line)
            try: 
                parser = PageParser(content['text'],"en")
            except KeyError:
                continue
            threads = parser.full_parse()
            pprint(threads)
            # pprint(content["text"])
            x = input()
        