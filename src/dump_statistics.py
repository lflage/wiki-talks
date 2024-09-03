import os
import orjson as json
import argparse
from log_utils import setup_logger
import sys
from pprint import pprint
_logger = setup_logger("dataset_statistics", "../logs/ds_statistics.log")


def get_all_keys(d):
    for key, value in d.items():
        if isinstance(value, dict):
            yield from get_all_keys(value)
        if isinstance(value, list):
            for reply in value:
                yield from get_all_keys(reply)
        else:
            yield value 

def max_replies_depth(conversation):
    if not conversation["replies"]:
        return 1
    else:
        return 1 + max(max_replies_depth(reply) for reply in conversation["replies"])


def dataset_statistics(path, out_folder="../experiments/ds_statistics/"):

    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
    out_path = os.path.join(out_folder, os.path.basename(path))

    if os.path.exists(out_path):
        print("file: {} already exists".format(out_path))
        return 

    with open(path, "r") as f:

        max_thread_n = {"n": 0,'url': str}
        max_thread_depth = 0
        max_comment_length = 0
        total_comment_length = 0 
        total_thread_n = 0
        total_depth = 0

        comment_n_total = 0
        max_comment_n = 0
        # try:
        for f in f.readlines():
            page_dict = json.loads(f)

            # total number of threads in the current json line
            total_thread_n += len(page_dict['threads'])
            # get max number of threads
            if len(page_dict['threads']) > max_thread_n['n']:
                max_thread_n['n'] = len(page_dict['threads'])
                max_thread_n['url'] = page_dict['url']

            # print(type(page_dict['threads']))
            for thread in page_dict['threads']:
                # get mean_comment_length
                # get max_comment_length
                # print(thread_list)
                # for thread in thread_list:
                comment_n_cur_thread = 0
                # if not isinstance(thread,dict):
                    # continue
                try:
                    for x in get_all_keys(thread):
                        if not x:
                            continue
                        # getting comment lenght in number of tokens
                        # print("--")
                        # print(x)
                        cur_list = x.split()
                        cur_len = len(cur_list)
                        # Max comment length
                        if cur_len > max_comment_length:
                            max_comment_length = cur_len
                        
                        total_comment_length += cur_len
                        comment_n_cur_thread += 1
                except AttributeError:
                    pprint(thread)
                    pprint(type(thread))
                    # pprint(x)
                    pprint(page_dict)
                    sys.exit()
                comment_n_total += comment_n_cur_thread
                if comment_n_cur_thread > max_comment_n:
                    max_comment_n = comment_n_cur_thread
                    max_comment_n_url = page_dict['url']
                        
                    
                # get max_thread_depth
                # get mean_thread_depth
                thread_depth_statistics = {}
                
                for thread in page_dict['threads']:
                    cur_depth = max_replies_depth(thread)
                    total_depth += cur_depth
                    if cur_depth > max_thread_depth:
                        max_thread_depth_url = page_dict['url']
                        max_thread_depth = cur_depth

        thread_length_statistics = {"max_comment_n": max_comment_n,
                                    "mean_comment_n": comment_n_total/total_thread_n,
                                    "max_comment_n_url": max_comment_n_url}

        thread_depth_statistics = {"max_depth_url": max_thread_depth_url,
                                    "max_thread_depth" : max_thread_depth,
                                    "mean_thread_depth": round(total_depth/total_thread_n,2)}

        comment_length_statistics ={'mean_comment_length': round(total_comment_length/comment_n_total,2),
                                'max_comment_length' : max_comment_length}

        stats_dict = {  "thread_length_statistics": thread_length_statistics,
                        "comment_length_statistics" : comment_length_statistics,
                        "max_thread_n": max_thread_n,
                        "thread_depth_statistics":thread_depth_statistics}
        print(stats_dict)
        print(out_path)
        with open(out_path, "wb") as f:
            f.write(json.dumps(stats_dict))
        # except:
            # print("Could not process {}".format(out_path))
            # _logger.debug("Could not process {}".format(out_path))
        


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=
        """Generates wiki-talks dataset statistics
        """)

    parser.add_argument('-o','--output', type=str, default="../experiments/ds_statistics/",
        help='path to output folder')
    parser.add_argument('-i','--in_folder', type=str,
        help='path to folder containing .jsonl files')

    args = parser.parse_args()

    dataset_statistics("../dataset/temp/piwiki-20240601-pages-meta-current.jsonl", args.output)
    print("ignored the first call")
    sys.exit()
    # path_to_jsonl = "../dataset/jsonl/dewiki-20240601-pages-meta-current.jsonl"
    for base,dirs,jsonl_list in os.walk(args.in_folder):
        for jsonl_file in jsonl_list:
            # print(base)
            # print(jsonl_file)
            json_path = os.path.join(base,jsonl_file)
            # print(json_path)
            dataset_statistics(json_path, args.output)
