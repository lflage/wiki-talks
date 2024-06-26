import requests
import os 

class WikiDumpDownloader:
    def __init__(self,  langs=[],
                        dump_date='20240601', 
                        out_folder='../dataset/raw/',
                        iso_code_path='../utils/ISO-639-2_utf-8.txt'):

        self.dump_date = dump_date
        self.iso_code_path = iso_code_path 
        self.out_folder = out_folder
        # Always read codes from file when initialiazing
        self.iso_639_dict = {}
        with open(self.iso_code_path,'r') as file:
            for line in file.readlines():
                codes = line.split('|')
                if codes[2]:
                    self.iso_639_dict[codes[2]] = codes[3]
        self.langs = langs or []


    def url_builder(self, lang_code):
        assert lang_code in self.iso_639_dict.keys()
        url = "https://dumps.wikimedia.org/{}wiki/{}/{}wiki-{}-pages-meta-current.xml.bz2".format(
            lang_code,
            self.dump_date,
            lang_code,
            self.dump_date
        )
        return url


    def download(self):
        print("Initializing donwload")
        # Check if languages were selected, else download wiki for all languages
        if self.langs:
            to_download = {k:v for (k, v) in self.iso_639_dict.items() if 
                                    self.iso_639_dict[k] in self.langs}
        else:
            to_download = self.iso_639_dict
        
        for lang_code in to_download.keys():
            # create Url
            url = self.url_builder(lang_code)
            # request download
            response = requests.get(url,stream=True)
            # create output path
            out_path = self.out_folder + url.split("/")[-1]
            # If file exists skip
            if os.path.exists(out_path):
                continue

            with open(out_path, 'wb') as out_f:
                for chunk in response.iter_content(chunk_size=10* 1024):
                    out_f.write(chunk)

if __name__ == "__main__":
    # Debbugging:
    downloader = WikiDumpDownloader(langs=['Portuguese','French'])
    downloader.wiki_dump_downloader()