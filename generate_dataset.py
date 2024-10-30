import os
import argparse
import multiprocessing
from tqdm import tqdm
from src.config import DATA_DIR
from src.utils.date_signatures import iso_639_dict
from src.core.wikitalkthreadparser import WikiTalkThreadParser
from src.core.wikidumpdownloader import WikiDumpDownloader
from src.utils.log_utils import setup_logger

# Set up argument parser for command-line arguments
parser = argparse.ArgumentParser(description="Generates wiki-talks dataset")

parser.add_argument('-o', '--output', type=str, default=DATA_DIR + '/datasets/v',
                    help='Path to output directory')
parser.add_argument('-i', '--raw_path', type=str, default=DATA_DIR + '/raw/',
                    help='Path to folder containing .bz2 files')
parser.add_argument('-d', '--dump_date', type=str, default='20240601',
                    help='Wikipedia dump date in the format YYYYMMDD')
parser.add_argument('-l', '--langs', nargs='*', type=str,
                    help='List of language codes to download')

args = parser.parse_args()

# Define paths and variables based on arguments
bz2_file_paths = args.raw_path
jsonl_file_paths = args.output
dump_date = args.dump_date
langs = args.langs if args.langs else []

# Create output directories for each language
# If langs is empty, creates for all languages in the iso_639_dict
languages_to_process = langs if langs else iso_639_dict

for code in languages_to_process:
    cur_path = os.path.join(jsonl_file_paths, code)
    if not os.path.exists(cur_path):
        os.makedirs(cur_path, exist_ok=True)

# Set up logger for generating dataset logs
gen_dataset_logger = setup_logger(__file__)

def multi(path):
    """Parses individual Wikipedia dump files and saves the output.
    Defined to be passed as function for multi-threading

    Args:
        path (str): Path to the .bz2 file to parse.
    """
    gen_dataset_logger.info(f"Started parsing: {path}")
    parser = WikiTalkThreadParser(out_folder=jsonl_file_paths)
    parser.parse_wikipedia_dump(path)
    gen_dataset_logger.info(f"Successfully parsed: {path}")

# Initialize WikiDumpDownloader to download Wikipedia dump files
downloader = WikiDumpDownloader(langs=langs,
                                dump_date=dump_date,
                                out_folder=bz2_file_paths)
downloader.download()

print("Finished downloading")

# Gather all .bz2 file paths for processing
f_paths = []
for root, dirnames, files in os.walk(bz2_file_paths):
    for file in files:
        f_path = os.path.join(root, file)
        if ".bz2" in f_path:
            f_paths.append(f_path)

# Set up multiprocessing pool with available CPU cores
num_items_to_process = len(f_paths)
pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

print(f"Using {multiprocessing.cpu_count()} cores/processes in parallel")

# Process files in parallel with a progress bar
with tqdm(total=num_items_to_process, desc="Processing files", dynamic_ncols=True) as pbar:
    for _ in pool.imap_unordered(multi, f_paths[:num_items_to_process]):
        pbar.update()
