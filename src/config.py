"""
Configuration module for defining project-wide paths.

This module provides absolute paths to directories and files used
across the codebase, including data, logs, and utility files.

Attributes:
    ROOT_DIR (str): Absolute path to the project root directory.
    DATA_DIR (str): Absolute path to the data directory.
    LOGS_DIR (str): Absolute path to the logs directory.
    ISO_CODE_PATH (str): Absolute path to the ISO language codes file.
    CHECKSUMS_DIR (str): Absolute path to the checksums directory.
"""

import os

# Defining paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
ISO_CODE_PATH = os.path.join(ROOT_DIR, 'src', 'utils', 'ISO-639-2_utf-8.txt')
CHECKSUMS_DIR = os.path.join(ROOT_DIR, 'src', 'utils', 'checksums')
