import os
import orjson as json
import argparse
import sys
from tqdm import tqdm
from pprint import pprint

""" 
This file exists to generate Dataset statistics. The statistics obtained here are the following:
- Total number of Threads                                                   # Each page contains multiple threads
- Total number of comments                                                  # number of total comments, either starting a thread or reponses
- Longest thread (highest number of messages in the same thread)            # Previously Max thread size
- Longest comment                                                           # Previously max comment length (tokens)
- Longest discussion (longest chain of responses to a message)              # Previously max thread depth
- avg thread length
- avg comment length
- avg discussion length
"""


def iter_messages(node):
    """Yield message text from a thread/reply node and all its descendants."""
    msg = node.get("message")
    if msg:
        yield msg
    msg = node.get("text")
    if msg:
        yield msg
    for reply in node.get("replies", []):
        yield from iter_messages(reply)

def max_replies_depth(conversation):
    if not conversation["replies"]:
        return 1
    else:
        return 1 + max(max_replies_depth(reply) for reply in conversation["replies"])

def accumulate_stats(stats, accum):
    accum['total_thread_n'] += stats['total_thread_n']
    accum['total_comment_n'] += stats['total_comment_n']
    accum['total_comment_length'] += stats['total_comment_length']
    accum['total_depth'] += stats['total_depth']

    for key in ('max_thread_n', 'max_comment_length', 'max_comment_n', 'max_thread_depth'):
        if stats[key]['n'] > accum[key]['n']:
            accum[key] = stats[key]

def get_averages(stats):
    stats["mean_comment_n"] = stats['total_comment_n'] / stats['total_thread_n'] if stats['total_thread_n'] else 0

    stats['mean_thread_depth'] = round(stats['total_depth'] / stats['total_thread_n'], 2) if stats['total_thread_n'] else 0

    stats['mean_comment_length'] = round(stats['total_comment_length'] / stats['total_comment_n'], 2) if stats['total_comment_n'] else 0

    return stats

def dataset_statistics(path):
    stats = {
        'total_thread_n': 0,
        'total_comment_n': 0,
        'total_comment_length': 0,
        'total_depth': 0,
        'max_thread_n': {'n': 0, 'url': ""},
        'max_comment_length': {'n': 0, 'url': ""},
        'max_comment_n': {'n': 0, 'url': ""},
        'max_thread_depth': {'n': 0, 'url': ""},
    }
    first = True

    with open(path, "r") as fh:
        for line in tqdm(fh):
            page_dict = json.loads(line)
            threads = page_dict['threads']
            url = page_dict['url']

            stats['total_thread_n'] += len(threads)
            if len(threads) > stats['max_thread_n']['n']:
                stats['max_thread_n'] = {'n': len(threads), 'url': url}

            for thread in threads:
                comment_n_cur_thread = 0
                for msg in iter_messages(thread):
                    cur_len = len(msg.split())
                    stats['total_comment_length'] += cur_len
                    if cur_len > stats['max_comment_length']['n']:
                        stats['max_comment_length'] = {'n': cur_len, 'url': url}
                    comment_n_cur_thread += 1

                stats['total_comment_n'] += comment_n_cur_thread
                if comment_n_cur_thread > stats['max_comment_n']['n']:
                    stats['max_comment_n'] = {'n': comment_n_cur_thread, 'url': url}

                cur_depth = max_replies_depth(thread)
                stats['total_depth'] += cur_depth
                if cur_depth > stats['max_thread_depth']['n']:
                    stats['max_thread_depth'] = {'n': cur_depth, 'url': url}
            if first:
                print(stats)
                first = False
    return stats


        


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=
        """Generates wiki-talks dataset statistics
        """)

    parser.add_argument('-o','--output', type=str, default="./experiments/ds_statistics/",
        help='path to output folder')
    parser.add_argument('-i','--input', type=str,
        help='path to input')
    parser.add_argument('-m','--mode', type=str, choices=['individual', 'full', 'combined'],
        default='individual', help='individual for one jsonl file, full a dir containing jsonl files, combined for all files together')

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    if args.mode == 'individual':
        """ for one jsonl file """
        assert os.path.isfile(args.input)

        OUTPUT_PATH = os.path.join(args.output, os.path.basename(args.input))
        print(OUTPUT_PATH)

        stats = dataset_statistics(args.input)
        get_averages(stats)

        with open(OUTPUT_PATH, "wb") as f:
            f.write(json.dumps(stats))

    if args.mode == 'full':
        """For a directory containing jsonl files i.e. language specific"""
        assert os.path.isdir(args.input)

        for base,dirs,jsonl_list in os.walk(args.input):
            for jsonl_file in jsonl_list:

                json_full_path = os.path.join(base,jsonl_file)

                stats = dataset_statistics(json_full_path)
                get_averages(stats)
       
                OUTPUT_PATH = os.path.join(args.output, os.path.basename(jsonl_file))

                with open(OUTPUT_PATH, "wb") as f:
                    f.write(json.dumps(stats))

    if args.mode == 'combined':
        """For all jsonl files in the dataset"""
        assert os.path.isdir(args.input)
        combined_stats = {
        'total_thread_n': 0,
        'total_comment_n': 0,
        'total_comment_length': 0,
        'total_depth': 0,
        'max_thread_n': {'n': 0, 'url': ""},
        'max_comment_length': {'n': 0, 'url': ""},
        'max_comment_n': {'n': 0, 'url': ""},
        'max_thread_depth': {'n': 0, 'url': ""},
        }
        first = True
        for base, dirs, jsonl_list in os.walk(args.input):
            for jsonl_file in tqdm(jsonl_list):
                if "sidecar" in jsonl_file or "checkpoint" in jsonl_file:
                    continue
                if not jsonl_file.endswith("jsonl"):
                    continue
                json_full_path = os.path.join(base, jsonl_file)
                print(json_full_path)
                stats = dataset_statistics(json_full_path)

                LANG_OUTPUT_PATH = os.path.join(args.output, os.path.basename(jsonl_file))
                with open(LANG_OUTPUT_PATH, "wb") as f:
                    f.write(json.dumps(get_averages(stats)))

                accumulate_stats(stats, combined_stats)
                if first:
                    print(combined_stats)
                    first = False

        # Compute final statistics
        get_averages(combined_stats)


        OUTPUT_PATH = os.path.join(args.output, "combined_stats.json")
        with open(OUTPUT_PATH, "wb") as f:
            f.write(json.dumps(combined_stats))

