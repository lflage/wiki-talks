import os
import orjson as json
import argparse
import sys
from tqdm import tqdm
from pprint import pprint


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


def accumulate_stats(stats, accum):
    # Accumulate statistics from one file into the running totals
    accum['total_thread_n'] += stats['total_thread_n']
    accum['comment_n_total'] += stats['comment_n_total']
    accum['total_comment_length'] += stats['total_comment_length']
    accum['total_depth'] += stats['total_depth']

    if stats['max_thread_n']['n'] > accum['max_thread_n']['n']:
        accum['max_thread_n'] = stats['max_thread_n']

    if stats['max_comment_length'] > accum['max_comment_length']:
        accum['max_comment_length'] = stats['max_comment_length']

    if stats['max_comment_n'] > accum['max_comment_n']:
        accum['max_comment_n'] = stats['max_comment_n']
        accum['max_comment_n_url'] = stats['max_comment_n_url']

    if stats['max_thread_depth'] > accum['max_thread_depth']:
        accum['max_thread_depth'] = stats['max_thread_depth']
        accum['max_thread_depth_url'] = stats['max_thread_depth_url']


def dataset_statistics(path, accumulate=False):

    with open(path, "r") as f:

        stats = {
            'total_thread_n': 0,
            'comment_n_total': 0,
            'total_comment_length': 0,
            'total_depth': 0,
            'max_thread_n': {'n': 0, 'url': str},
            'max_comment_length': 0,
            'max_comment_n': 0,
            'max_comment_n_url': None,
            'max_thread_depth': 0,
            'max_thread_depth_url': None,
        }

        for f in f.readlines():
            page_dict = json.loads(f)

            # total number of threads in the current json line
            stats['total_thread_n'] += len(page_dict['threads'])
            # get max number of threads
            if len(page_dict['threads']) > stats['max_thread_n']['n']:
                stats['max_thread_n']['n'] = len(page_dict['threads'])
                stats['max_thread_n']['url'] = page_dict['url']

            for thread in page_dict['threads']:
                # get mean_comment_length
                # get max_comment_length
                comment_n_cur_thread = 0
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
                        if cur_len > stats['max_comment_length']:
                            stats['max_comment_length'] = cur_len
                        
                        stats['total_comment_length'] += cur_len
                        comment_n_cur_thread += 1
                except AttributeError:
                    pprint(thread)
                    pprint(type(thread))
                    # pprint(x)
                    pprint(page_dict)
                    sys.exit()
                stats['comment_n_total'] += comment_n_cur_thread
                if comment_n_cur_thread > stats['max_comment_n']:
                    stats['max_comment_n'] = comment_n_cur_thread
                    stats['max_comment_n_url'] = page_dict['url']
                        
                    
                # get max_thread_depth
                # get mean_thread_depth
                thread_depth_statistics = {}
                
                for thread in page_dict['threads']:
                    cur_depth = max_replies_depth(thread)
                    stats['total_depth'] += cur_depth
                    if cur_depth > stats['max_thread_depth']:
                        max_thread_depth_url = page_dict['url']
                        stats['max_thread_depth'] = cur_depth

        stats['thread_length_statistics'] = {
            "max_comment_n": stats['max_comment_n'],
            "mean_comment_n": stats['comment_n_total'] / stats['total_thread_n'] if stats['total_thread_n'] else 0,
            "max_comment_n_url": stats['max_comment_n_url']
        }
        stats['thread_depth_statistics'] = {
            "max_depth_url": stats['max_thread_depth_url'],
            "max_thread_depth": stats['max_thread_depth'],
            "mean_thread_depth": round(stats['total_depth'] / stats['total_thread_n'], 2) if stats['total_thread_n'] else 0
        }
        stats['comment_length_statistics'] = {
            'mean_comment_length': round(stats['total_comment_length'] / stats['comment_n_total'], 2) if stats['comment_n_total'] else 0,
            'max_comment_length': stats['max_comment_length']
        }
        print(stats)
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

    if args.mode == 'individual':
        assert os.path.isfile(args.input)

        OUTPUT_PATH = os.path.join(args.output, os.path.basename(args.input))

        stats_dict = dataset_statistics(args.input)

        with open(OUTPUT_PATH, "wb") as f:
            f.write(json.dumps(stats_dict))

    if args.mode == 'full':
        assert os.path.isdir(args.input)

        for base,dirs,jsonl_list in os.walk(args.input):
            for jsonl_file in jsonl_list:

                json_full_path = os.path.join(base,jsonl_file)

                stats_dict = dataset_statistics(json_full_path)

                OUTPUT_PATH = os.path.join(args.output, os.path.basename(jsonl_file))
       
                with open(OUTPUT_PATH, "wb") as f:
                    f.write(json.dumps(stats_dict))

    if args.mode == 'combined':
        assert os.path.isdir(args.input)
        combined_stats = {
            'total_thread_n': 0,
            'comment_n_total': 0,
            'total_comment_length': 0,
            'total_depth': 0,
            'max_thread_n': {'n': 0, 'url': str},
            'max_comment_length': 0,
            'max_comment_n': 0,
            'max_comment_n_url': None,
            'max_thread_depth': 0,
            'max_thread_depth_url': None,
        }
        for base, dirs, jsonl_list in os.walk(args.input):
            for jsonl_file in tqdm(jsonl_list):
                json_full_path = os.path.join(base, jsonl_file)
                stats = dataset_statistics(json_full_path)
                accumulate_stats(stats, combined_stats)
        # Compute final statistics
        combined_stats['thread_length_statistics'] = {
            "max_comment_n": combined_stats['max_comment_n'],
            "mean_comment_n": combined_stats['comment_n_total'] / combined_stats['total_thread_n'] if combined_stats['total_thread_n'] else 0,
            "max_comment_n_url": combined_stats['max_comment_n_url']
        }
        combined_stats['thread_depth_statistics'] = {
            "max_depth_url": combined_stats['max_thread_depth_url'],
            "max_thread_depth": combined_stats['max_thread_depth'],
            "mean_thread_depth": round(combined_stats['total_depth'] / combined_stats['total_thread_n'], 2) if combined_stats['total_thread_n'] else 0
        }
        combined_stats['comment_length_statistics'] = {
            'mean_comment_length': round(combined_stats['total_comment_length'] / combined_stats['comment_n_total'], 2) if combined_stats['comment_n_total'] else 0,
            'max_comment_length': combined_stats['max_comment_length']
        }
        OUTPUT_PATH = os.path.join(args.output, "combined_stats.json")
        with open(OUTPUT_PATH, "wb") as f:
            f.write(json.dumps(combined_stats))

