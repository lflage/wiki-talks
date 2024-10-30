"""
Module containing language-specific date parsing patterns and ISO 639 language codes.
date_sign_dict is easily acessible for public contributions

This file contains:
    - `date_sign_dict`: A dictionary containing regular expression patterns for parsing 
      date signatures in Wikipedia talk pages for different languages. The keys are 
      ISO 639-1 language codes, and values are regex patterns to identify date formats.
    - `iso_639_dict`: A dictionary mapping ISO 639-1 language codes to language names, 
      dynamically populated from a file located at `ISO_CODE_PATH`.

Example:
    Use `date_sign_dict` to retrieve the date format regex for a specific language:
    
        en_pattern = date_sign_dict['en']
"""

from ..config import ISO_CODE_PATH

date_sign_dict = {
"en" : r"\d{1,2}:\d{2}, \d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \(UTC\)",
"pt" : r"(\d{2})h(\d{2})min de (\d{2}) de (\w+) de (\d{4}) \(\w+\)",
"fr" : r"(\d{1,2}) (\w+) (\d{4}) à (\d{2}):(\d{2}) \(\w+\)",
"de" : r"(\d{2}):(\d{2}), (\d{1,2})\. (\w+)\.? (\d{4}) \(\w+\)",
"es" : r"(\d{2}):(\d{2}) (\d{1,2}) (\w{3}) (\d{4}) \(\w+\)",
"it" : r"(\d{2}):(\d{2}), (\d{1,2}) (\w{3}) (\d{4}) \(\w+\)",
}

# Always read codes from file when initialiazing

iso_639_dict = {}
with open(ISO_CODE_PATH, 'r', encoding='utf-8') as file:
    for line in file.readlines():
        codes = line.split('|')
        if codes[2]:
            iso_639_dict[codes[2]] = codes[3]
