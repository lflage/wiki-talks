# TODO: Module Docstring
import sys
import json
from pprint import pprint


def thread_parse_debug(cur_dict, targe_file="../tests/debug.jsonl"):
    pprint(cur_dict)
    x = input()
    if x == "s":
        with open(targe_file, 'a', encoding='utf8') as f_out:
            json.dump(cur_dict, f_out)
            f_out.write('\n')
    if x == "n":
        return
    if x == "q":
        sys.exit()
