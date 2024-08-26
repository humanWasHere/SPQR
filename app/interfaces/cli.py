import argparse
import logging
import sys
from pathlib import Path

from .. import __version__


def parse_intervals(values: list[str]) -> list[list[int]]:
    if values is None:
        return None
    list_of_lists = []
    for value in values:
        try:
            if '-' not in value:
                raise ValueError("Separator must be a hyphen")
            start, end = map(int, value.split('-'))
            list_of_lists.append([start, end])
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"Each range must be in the format 'start-end'. Error: {e}")
    return list_of_lists


def cli() -> argparse.ArgumentParser:
    """defines the command lines actions of the soft"""
    parser = argparse.ArgumentParser(prog='spqr',
                                     description='----- CLI tool for SEM Recipe Creation -----')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    subparsers = parser.add_subparsers(
        dest='running_mode',
        help='Selects the running mode of the app (test, init or build). End user should use build.')

    test_parser = subparsers.add_parser(
        'test', help='Runs the "testing" mode of the app. Meant for app developers.')
    test_parser.add_argument('-r', '--recipe',
                              help='Runs the recipe inputted (genepy, calibre_rulers, opcfield, csv or json) in testing mode. Refer to app_config.json.',
                              choices=['genepy', 'calibre_rulers', 'opcfield', 'csv', 'json'],
                              type=str)
    test_parser.add_argument('-a', '--all_recipes', action="store_true",
                              help='Runs all recipes (genepy, calibre_rulers, opcfield, csv and json) in testing mode. Refer to app_config.json.')

    build_parser = subparsers.add_parser(
        'build', help='Runs the "prod" mode of the app. Meant for end user.')
    build_parser.add_argument('-c', '--user_config', required=True, type=Path,
                              help="Path to user JSON config file containing recipe options.")
    build_parser.add_argument('-r', '--user_recipe',
                              help='Runs the recipe inputted if it is matching one in user_config.json. Refer to this file')
    build_parser.add_argument('-u', '--upload_rcpd', action="store_true",
                              help='Send HSS recipe (.csv) and layout to RecipeDirector machine.')
    build_parser.add_argument('-l', '--line_selection', required=False, nargs='+', type=str,
                              help='Allows user to run a recipe creation with a selected range of lines. Must be written like so : "-l 50-60 150-160" where 50 and 60 are included as well as 150 and 160')
    build_parser.add_argument('-m', '--mesurement_file', action="store_true",
                              help='Outputs the measurement file to user outputs directory')
    
    init_parser = subparsers.add_parser(
        'init', help='Creates a default user configuration file in json under given path.')
    init_parser.add_argument('-c', '--config_file_path', required=True, type=Path,
                              help='Takes a path to make a default user configuration file in json under given path.')
    init_parser.add_argument('-p', '--coordinate_file', action="store_true",
                              help='Creates a generic coordinate source file (ssfile format).')

    return parser


def check_recipe(full_config: dict[str, dict], recipe_name: str) -> dict:
    if len(full_config) == 0:
        raise ValueError("The provided configuration file does not contain any recipe.")
    elif len(full_config) == 1 and recipe_name is None:
        # recipe name is optional if there is only one
        recipe_name = next(iter(full_config.keys()))
    elif len(full_config) > 1 and recipe_name is None:
        logging.warning("More than one recipe found in the configuration file. Please select one with the -r option.")
        sys.exit(1)

    if recipe_name not in full_config:
        logging.error(f'TU QUOQUE FILI !? Recipe {recipe_name} not found in the JSON config file.')
        sys.exit(1)

    return full_config[recipe_name]