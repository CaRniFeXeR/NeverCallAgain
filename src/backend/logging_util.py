import os
import uuid
from pathlib import Path
from logging import FileHandler, Formatter
from typing import Any, Dict, Mapping, Tuple, Union, Optional
import logging

LOGGING_FORMAT = '%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s'

logging.basicConfig(
    format=LOGGING_FORMAT,
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
)
def_logger = logging.getLogger()


def uniquify(path) -> str:
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path


def make_dirs(dir_path):
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def make_parent_dirs(file_path):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def setup_log_file(log_file_path, mode='w'):
    make_parent_dirs(log_file_path)
    fh = FileHandler(filename=log_file_path, mode=mode)
    fh.setFormatter(Formatter(LOGGING_FORMAT))
    def_logger.addHandler(fh)


def prepare_log_file(log_file_path, overwrite=False):
    if overwrite:
        log_file_path = uniquify(log_file_path)
        mode = 'w'
    else:
        mode = 'a'
    setup_log_file(os.path.expanduser(log_file_path), mode=mode)
