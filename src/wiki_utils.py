import requests
import pprint

dump_date='20240601'

iso_639_dict = {}
with open('../utils/ISO-639-2_utf-8.txt','r') as file:
    for line in file.readlines():
        codes = line.split('|')
        iso_639_dict[codes[2]] = codes[3]

def url_builder(lang_code,dump_date='20240601'):
    assert lang_code in iso_639_dict.keys()
    url = "https://dumps.wikimedia.org/{}wiki/{}/{}wiki-{}-pages-meta-current.xml.bz2".format(
        lang_code,
        dump_date,
        lang_code,
        dump_date
    )
    return url


def wiki_dump_downloader():
    for lang_code in iso_639_dict.keys():
        url = url_builder(lang_code)
        response = requests.get(url,stream=True)
        with open("../dataset/"+ url.split("/")[-1], 'wb') as out_f:
            for chunk in response.iter_content(chunk_size=10* 1024):
                out_f.write(chunk)