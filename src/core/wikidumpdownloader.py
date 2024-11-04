import os
import hashlib
import requests
from ..config import ISO_CODE_PATH, CHECKSUMS_DIR
from ..utils.date_signatures import iso_639_dict


class WikiDumpDownloader:
    """
    Downloads Wikipedia dumps and verifies their checksums for specified languages and dates.

    Attributes:
        langs (list): List of language names to download, if empty downloads for all languages.
        dump_date (str): Date of the Wikipedia dump to download (formatted as 'YYYYMMDD').
        out_folder (str): Path to the output folder for storing downloaded dumps.
        iso_code_path (str): Path to the ISO code file containing language codes.
        checksums_path (str): Path to the directory for checksum files.
        hash_download (bool): Flag indicating if hash files have been downloaded.
        iso_639_dict (dict): Dictionary mapping language codes to language names.
    """

    def __init__(self,
                langs=None,
                dump_date='20240601',
                out_folder='../data/raw/',
                iso_code_path=ISO_CODE_PATH,
                checksums_path=CHECKSUMS_DIR):
        """
        Initializes the WikiDumpDownloader with specified download settings.

        Args:
            langs (list, optional): List of languages to download. Defaults to None.
            dump_date (str): Dump date in 'YYYYMMDD' format. Defaults to '20240601'.
            out_folder (str): Output directory for downloaded dumps. Defaults to '../dataset/raw/'.
            iso_code_path (str): Path to ISO codes. Defaults to ISO_CODE_PATH.
            checksums_path (str): Path to checksum files directory. Defaults to CHECKSUMS_DIR.
        """
        self.dump_date = dump_date
        self.iso_code_path = iso_code_path
        self.out_folder = out_folder
        self.checksums_path = checksums_path
        self.hash_download = False
        self.iso_639_dict = iso_639_dict
        self.langs = [] if langs is None else langs

    def url_builder(self, lang_code):
        """
        Builds the URL for downloading a Wikipedia dump based on language and date.

        Args:
            lang_code (str): ISO code for the language to download.

        Returns:
            str: The URL to download the specified Wikipedia dump.
        """
        assert lang_code in self.iso_639_dict
        url = '''
        https://dumps.wikimedia.org/{lg_code}wiki/{date}/{lg_code}wiki-{date}-pages-meta-current.xml.bz2
        '''.format(lg_code=lang_code, date=self.dump_date)
        return url

    def download_hashes(self):
        """
        Downloads MD5 hash files for each language's Wikipedia dump to the checksums directory.
        
        If the checksum file already exists, it skips the download.
        """
        for lang_code in self.iso_639_dict:
            url = '''
            https://dumps.wikimedia.org/{lg_code}wiki/{date}/{lg_code}wiki-{date}-md5sums.txt
            '''.format(lg_code=lang_code, date=self.dump_date)
            # Create output path
            out_path = os.path.join(self.checksums_path, url.split("/")[-1])
            # Skip if file exists
            if os.path.exists(out_path):
                continue
            # Request download
            response = requests.get(url, stream=True, timeout=10)
            if not response.ok:
                print(f"Could not download: {url}")
                continue

            with open(out_path, 'w', encoding='utf-8') as out_f:
                out_f.write(response.text)
        self.hash_download = True

    def get_hash(self, lang_code):
        """
        Retrieves the MD5 checksum for a specified language's Wikipedia dump.

        Args:
            lang_code (str): ISO code of the language.

        Returns:
            str: The MD5 checksum for the Wikipedia dump file.

        Raises:
            FileNotFoundError: If the checksum file for the language does not exist.
        """
        file = self.url_builder(lang_code).split("/")[-1]
        path = os.path.join(self.checksums_path, f"{lang_code}wiki-{self.dump_date}-md5sums.txt")

        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as checksum_file:
                for line in checksum_file.readlines():
                    try:
                        checksum, file_name = line.split()
                    except ValueError:
                        print(line)
                        print(file)
                        raise ValueError("Error parsing checksum line")
                    if file_name == file:
                        return checksum
        else:
            print(f"Checksum file not found: {path}")
            raise FileNotFoundError

    def hash_checker(self, file_path):
        """
        Verifies the MD5 checksum of a downloaded Wikipedia dump file.

        Args:
            file_path (str): Path to the downloaded Wikipedia dump file.

        Raises:
            FileNotFoundError: If hash files haven't been downloaded.
            AssertionError: If the file hash does not match the expected hash.
        """
        if not self.hash_download:
            print("No hash files downloaded")
            raise FileNotFoundError

        lang_code = file_path.split('/')[-1][:2]
        wiki_md5 = self.get_hash(lang_code)

        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            while chunk := f.read(320 * 1024):
                file_hash.update(chunk)
        try:
            assert wiki_md5 == file_hash.hexdigest()
            print(f"Hash verification complete: {file_path}")
        except AssertionError:
            print(f"Hash verification failed for: {file_path}")
            # TODO: Add a logging system for failed verifications

    def download(self):
        """
        Downloads Wikipedia dump files for the specified languages to the output folder.
        
        If no languages are specified, downloads for all languages in `iso_639_dict`.
        Skips download if the file already exists.
        """
        print("Initializing download")

        # Check if specific languages were provided
        if self.langs:
            to_download = {k: v for k, v in self.iso_639_dict.items() if v in self.langs}
        else:
            to_download = self.iso_639_dict

        for lang_code in to_download.keys():
            # Build URL
            url = self.url_builder(lang_code)
            # Request download
            response = requests.get(url, stream=True, timeout=10)
            if not response.ok:
                continue

            # Create output path
            out_path = os.path.join(self.out_folder, url.split("/")[-1])
            # Skip if file already exists
            if os.path.exists(out_path):
                continue

            with open(out_path, 'wb') as out_f:
                for chunk in response.iter_content(chunk_size=10 * 1024):
                    out_f.write(chunk)


if __name__ == "__main__":
    # Debugging example
    downloader = WikiDumpDownloader(langs=['Portuguese', 'French'])
    downloader.download()
