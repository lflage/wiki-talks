import os, argparse,bz2
from process_iterparse import parse_wikipedia_dump
from wiki_utils import WikiDumpDownloader

parser = argparse.ArgumentParser(description=
        """Generates wiki-talks dataset
        """)

parser.add_argument('-o','--output', type=str, default='../dataset/jsonl/',
        help='path to output' )
parser.add_argument('-i','--raw_path', type=str, default='../dataset/raw/',
        help='path to folder containing .bzw files')
parser.add_argument('-d', '--dump_date', type=str, default='20240601',
        help='dumpdate')
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

# Download wiki dump files from wikiserver
downloader = WikiDumpDownloader(langs=langs,
                                dump_date=dump_date,
                                out_folder=bz2_file_paths)
downloader.download()


# # process files for generating jsonl/parser dataset
# f_paths = []
# for root, dirnames, files in os.walk():
#     for file in files:
#         if ".bz2" in file:
#             f_paths.append(os.path.join(root,file))
# 
# # parse each dump
# for path in f_paths:
#     with bz2.BZ2File(path, 'rb') as f:
#         parse_wikipedia_dump(f)