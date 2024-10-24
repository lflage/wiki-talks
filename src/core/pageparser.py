import re
from pprint import pprint
import wikitextparser as wtp
from .dict_tree import thread_tree, thread_no_title
from ..utils.date_signatures import date_sign_dict

header = r"(={2,6})(.*?)(\1)"
ruler = r"\n-{4,}"


class PageParser():
    def __init__(self, to_parse, lang):
        self.attempts = 0
        self.to_parse = to_parse
        self.lang = lang

        # If there is a date signature regex, use the date signature to mark end of comment
        # else use the colon marking the next comment to mark end of initial comment
        if self.lang in date_sign_dict.keys():
            self.main_parse_function = thread_tree
        else:
            self.main_parse_function = thread_no_title
        

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
                        # Gets all threads before the first header
                        for thread_text in re.split(ruler, trailing_text):
                            cur_thread = thread_no_title(thread_text,self.lang)
                            threads_list.append(cur_thread)

                        # Parses from the first header forward
                        threads_list.extend(self.wtp_parse(match.string[match.start():]))
                    # TODO: This else should not parse self.to_parse, but what
                    #  comes after the first header 
                    else:
                        threads_list.extend(self.wtp_parse(self.to_parse))

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

            section_txt += "\n" + wtp.remove_markup(sec_text)

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
        