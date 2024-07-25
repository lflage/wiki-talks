import sys
import json
from pprint import pprint

debug_file = "../tests/debug.jsonl"

def thread_parse_debug(cur_dict):
    pprint(cur_dict)
    x = input()
    if x == "s":
        with open(debug_file, 'a') as f_out:
            json.dump(cur_dict, f_out)
            f_out.write('\n')
    if x == "n":
       return 
    if x == "q":
        sys.exit()