import os
import argparse
import multiprocessing
from tqdm import tqdm
from wikitalkthreadparser import WikiTalkThreadParser
from wikidumpdownloader import WikiDumpDownloader
from log_utils import setup_logger

parser = argparse.ArgumentParser(description=
        """Generates wiki-talks dataset
        """)

parser.add_argument('-o','--output', type=str, default='../dataset/jsonl/',
        help='path to output' )
parser.add_argument('-i','--raw_path', type=str, default='../dataset/raw/',
        help='path to folder containing .bz2 files')
parser.add_argument('-d', '--dump_date', type=str, default='20240601',
        help='dumpdate in the format YYYYMMDD')
parser.add_argument('-l', '--langs', nargs='*' ,type=str,
        help='list of languages to download')

args = parser.parse_args()

bz2_file_paths = args.raw_path
jsonl_file_paths = args.output
dump_date = args.dump_date
if not args.langs:
    langs = []
else:
    langs = args.langs
# Configure gen_dataset_logger
gen_dataset_logger = setup_logger("generate_dataset", "../logs/generate_dataset.log")

def multi(path):
    gen_dataset_logger.info("Started parsing: {}".format(path))
    parser = WikiTalkThreadParser(out_folder=jsonl_file_paths,)
    parser.parse_wikipedia_dump(path)
    gen_dataset_logger.info("Succesfully parsed: {}".format(path))

# Download wiki dump files from wikiserver
downloader = WikiDumpDownloader(langs=langs,
                                dump_date=dump_date,
                                out_folder=bz2_file_paths)
downloader.download()

print("finished donwloading")
# process files for generating jsonl/parser dataset
f_paths = []
for root, dirnames, files in os.walk(bz2_file_paths):
    for file in files:
        f_path = os.path.join(root,file)
        if ".bz2" in f_path:
            f_paths.append(f_path)

# Initialize a Pool with the number of available processors
num_items_to_process=len(f_paths)
pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

print(f"Using {multiprocessing.cpu_count()} cores/processes in parallel")
     # Use Pool's map function to process the items in parallel


with tqdm(total=num_items_to_process, desc="Processing files", dynamic_ncols=True) as pbar:
    for _ in pool.imap_unordered(multi, f_paths[:num_items_to_process]):
        pbar.update()
print("started parsing")