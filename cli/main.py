import tempfile
import argparse
import click
import json
import sys
import os
from subprocess import call

from appdirs import *
from pathlib import Path
from rich import print
from itertools import chain


FUNNY_TEXT = """

░█████╗░░█████╗░███╗░░██╗███████╗██╗░██████╗░
██╔══██╗██╔══██╗████╗░██║██╔════╝██║██╔════╝░
██║░░╚═╝██║░░██║██╔██╗██║█████╗░░██║██║░░██╗░
██║░░██╗██║░░██║██║╚████║██╔══╝░░██║██║░░╚██╗
╚█████╔╝╚█████╔╝██║░╚███║██║░░░░░██║╚██████╔╝
░╚════╝░░╚════╝░╚═╝░░╚══╝╚═╝░░░░░╚═╝░╚═════╝░
"""


APP_NAME, APP_AUTHOR = "Sardine", "Bubobubobubo"
USER_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
CONFIG_JSON = USER_DIR / "config.json"


def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


def read_json_file():
    """Read JSON File (configuration file)"""
    with open(str(CONFIG_JSON), "r") as jsonFile:
        return json.load(jsonFile)


def write_json_file(data: dict):
    """Write to JSON File (configuration file)"""
    with open(str(CONFIG_JSON), "w") as jsonFile:
        json.dump(data, jsonFile)


def main():
    """Entry method for the argparse parser"""

    # Check if the configuration file exists, otherwise, warn user
    if not CONFIG_JSON.is_file():
        print(f"[red]The configuration file is missing.\
 Please boot Sardine first.")
        exit()
    data = read_json_file()

    parser = argparse.ArgumentParser(description="Sardine configuration CLI")
    parser.add_argument('--midi', type=str, help="Default MIDI port")
    parser.add_argument('--bpm', type=float, help="Beats per minute")
    parser.add_argument('--beats', type=int, help="Beats per bar")
    parser.add_argument('--ppqn', type=float, help="ppqn")
    parser.add_argument('--parameters', type=str, help="add a custom param")
    parser.add_argument('--boot', type=bool, help="Boot SC && SuperDirt")
    parser.add_argument('--deferred', type=bool,
            help="Turn on/off deferred scheduling")
    parser.add_argument('--clock', type=bool, help="Active or passive Clock")
    parser.add_argument('--SCconfig', type=bool,
            help="SuperDirt Configuration Path")
    parser.add_argument('--User Config Path', type=bool,
            help="Python User Configuration file")

    if len(sys.argv) < 2:
        print(f"[red]{FUNNY_TEXT}")
        print(f"Your configuration file is located at: {USER_DIR}")
        parser.print_help()
        exit()

    args = parser.parse_args()
    to_update = list(chain.from_iterable([x for x in args._get_kwargs()]))

    # Iterating over the collected kwargs and write to file if needed
    for name, value in pairwise(to_update):
        if value is not None:
            data['config'][name] = value
    write_json_file(data)



def _edit_configuration(file_name: str):
    configuration_file = USER_DIR / file_name
    # If the file already exists, we will read it first before opening editor
    if configuration_file.is_file():
        with open(configuration_file, 'r') as config:
            file_content = config.read()
        edited = click.edit(file_content)
        if edited is not None:
            with open(configuration_file, 'w') as config:
                config.write(edited)
    else:
        with open(configuration_file, 'w') as config:
            config.write('')
        # recurse to write in the file
        _edit_configuration(file_name)


def edit_python_configuration():
    """Call $EDITOR to edit Python based user configuration"""
    _edit_configuration("user_configuration.py")


def edit_superdirt_configuration():
    """Call $EDITOR to edit Python based user configuration"""
    _edit_configuration("default_superdirt.scd")


if __name__ == "__main__":
    main()
