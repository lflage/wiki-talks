# TODO: Module docstring

import os

# Defining paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
ISO_CODE_PATH = os.path.join(ROOT_DIR, 'src', 'utils', 'ISO-639-2_utf-8.txt')
CHECKSUMS_DIR = os.path.join(ROOT_DIR, 'src','utils', 'checksums')
