import requests
import hashlib
import os 

class WikiDumpDownloader:
    def __init__(self,  langs=[],
                        dump_date='20240601', 
                        out_folder='../dataset/raw/',
                        iso_code_path='../utils/ISO-639-2_utf-8.txt',
                        checksums_path='../utils/checksums/'):

        self.dump_date = dump_date
        self.iso_code_path = iso_code_path 
        self.out_folder = out_folder
        self.checksums_path = checksums_path
        self.hash_download = False

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
    
    def donwload_hashes(self):
        for lang_code in self.iso_639_dict.keys():
            url = "https://dumps.wikimedia.org/{}wiki/{}/{}wiki-{}-md5sums.txt".format(
            lang_code,
            self.dump_date,
            lang_code,
            self.dump_date
            )
            # create output path
            out_path = self.checksums_path + url.split("/")[-1]
            # If file exists skip
            if os.path.exists(out_path):
                continue
            # request download
            response = requests.get(url,stream=True)
            
            if not response.ok:
                print("Could not download: {}".format(url))
                continue

            with open(out_path, 'w') as out_f:
                out_f.write(response.text)
        self.hash_download = True

    def get_hash(self,lang_code):
        file = self.url_builder(lang_code).split("/")[-1]
        path = "../utils/checksums/{}wiki-{}-md5sums.txt".format(
            lang_code,
            self.dump_date
        )
        if os.path.exists(path):
            with open(path, "r") as checkum_file:
                for line in checkum_file.readlines():
                    try:
                        checksum , file_name = line.split()
                    except ValueError:
                        print(line)
                        print(file)
                        raise ValueError
                    if file_name == file:
                        return checksum
        else:
            print(path)
            print(file)
            raise FileNotFoundError

    def hash_checker(self, file_path):
        if not self.hash_download:
            print("No hash files downloaded")
            raise FileNotFoundError

        # TODO: find a better way to find the lang_codes
        lang_code = file_path.split('/')[-1][:2]
        wiki_md5 = self.get_hash(lang_code)

        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()

            while chunk := f.read(320*1024):
                file_hash.update(chunk)
        try:
            assert wiki_md5 == file_hash.hexdigest()
            print("hash complete: {}".format(file_path))
        except AssertionError:
            print("could not verify hash for: {}".format(file_path))
            # TODO: add a log

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