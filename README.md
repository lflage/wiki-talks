# wiki-talks

This repository contains code related to the Wiki-Talks dataset.
Dumps can be accessed at the Wikimedia [index(https://dumps.wikimedia.org/backup-index.html)]
An example of the wikipedia dumps used are the [following](https://dumps.wikimedia.org/simplewiki/20241020/):

```
2024-06-09 08:19:11 done All pages, current versions only.
simplewiki-20240601-pages-meta-current.xml.bz2 382.0 MB
```

# Usage
## Generate Dataset
The standard dataset is generated with the script ```generate_dataset.py```
It handles downloading, parsing and storing the data.

```
python ./generate_dataset.py
```

Defaults are:
```
--output DATA_DIR+/datasets/v
--raw_path DATA_DIR+/raw/
--dump_date 20240601
--langs 
```

 
## Downloading

Downloading is handled by the `WikiDumpDownloader` class.
The downloader can handle multiple languages, verify the integrity of downloaded files using MD5 checksums, and allows for efficient storage of files by skipping re-downloads if the file already exists.

### Standard Inputs

- `langs`: `list` of language names to download, e.g., `['Portuguese', 'French']`, if not set 
- `dump_date`: `str` specifying the date of the Wikipedia dump in `YYYYMMDD` format, e.g., `'20240601'`
- `out_folder`: `str` representing the path for the output directory, e.g., `'../data/raw/'`
- `iso_code_path`: `str` path to the ISO code file, e.g., `ISO_CODE_PATH`
- `checksums_path`: `str` path to the directory for checksum files, e.g., `CHECKSUMS_DIR`

If languages are not specificed, downloads all languages in the ISO-639-2 code standard.
## Parsing

### Dump Parsing

Using the WikiTalkThreadParser one can parse a Wikipedia XML dump of the [wikipedia Talks Pages](https://en.wikipedia.org/wiki/Help:Talk_pages), the data is obtained from the following keys:

- ns: namespace
- title: page title
- text: page content

It saves a unique `id` for each page and builds the `url` for the page.
The page textual content is passed to a new parser that retrives the threads structure.

### Page Parsing

The PageParser reads the content of the page and returns each thread as a dictionary containing the `title`, `message` and `replies`.
Each reply contains its own `message` and a list of `reply` dictionaries.

# Thread  Structure

```
thread = { "title": str,
			"message": str,
			"replies: list[reply]}
reply = { "message": str,
	       replies: list[reply]}
```

# Contribute

The main contribution from the community stems from defining the proper regex pattern for time signatures for each language.

Please open a pull request if you can contribute.

# License

See LICENSE file

# HuggingFace download

To download and use the standard Dataset refer to the [HuggingFace](https://huggingface.co/datasets/lflage/wiki-talks) page.