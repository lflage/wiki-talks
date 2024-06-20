# wiki-talks

This repository contains code related to the Wiki-Talks dataset.

An example of the wikipedia dumps used are the [following](http://wikipedia.c3sl.ufpr.br/simplewiki/20240601/):

```
2024-06-09 08:19:11 done All pages, current versions only.
simplewiki-20240601-pages-meta-current.xml.bz2 382.0 MB
```

# Usage

The main file in this repository is the following file

```
python ./src/process_iterparse.py
```
 
It parses a Wikipedia XML dump of the [wikipedia Talks Pages](https://en.wikipedia.org/wiki/Help:Talk_pages) for the following keys:
- ns: namespace
- title: page title
- text: page content
- id: #check if wikipages have an id 


# Example Code

TODO

# Example Structure

TODO