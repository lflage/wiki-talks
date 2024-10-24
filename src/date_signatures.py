# File containing relevat datastructures and paths

date_sign_dict = {
"en" : r"\d{1,2}:\d{2}, \d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \(UTC\)",
"pt" : r"(\d{2})h(\d{2})min de (\d{2}) de (\w+) de (\d{4}) \(\w+\)",
"fr" : r"(\d{1,2}) (\w+) (\d{4}) à (\d{2}):(\d{2}) \(\w+\)",
"de" : r"(\d{2}):(\d{2}), (\d{1,2})\. (\w+)\.? (\d{4}) \(\w+\)",
"es" : r"(\d{2}):(\d{2}) (\d{1,2}) (\w{3}) (\d{4}) \(\w+\)",
"it" : r"(\d{2}):(\d{2}), (\d{1,2}) (\w{3}) (\d{4}) \(\w+\)",
}

# Always read codes from file when initialiazing
ISO_CODE_PATH = '../utils/ISO-639-2_utf-8.txt'
iso_639_dict = {}
with open(ISO_CODE_PATH, 'r', encoding='utf-8') as file:
    for line in file.readlines():
        codes = line.split('|')
        if codes[2]:
            iso_639_dict[codes[2]] = codes[3]
