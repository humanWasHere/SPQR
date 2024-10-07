import argparse
import logging
import sys
from pathlib import Path

from .. import __version__


def parse_intervals(values: list[str] | None) -> list[list[int]] | None:
    """Convert CLI interval format to internal format, e.g. "1-10 20-30" -> [[1,10], [20,30]]"""
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
            raise argparse.ArgumentTypeError(
                f"Each range must be in the format 'start-end'. Error: {e}")
    return list_of_lists


def cli() -> argparse.ArgumentParser:
    """Defines the command lines actions of the soft."""
    DOC_PATH = Path(__file__).resolve().parents[2] / 'docs' / '_build' / 'html' / 'index.html'
    parser = argparse.ArgumentParser(
        prog='spqr',
        description='----- CLI tool for SEM Recipe Creation -----',
        epilog=f'For full documentation, visit {DOC_PATH}',
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(
        dest='running_mode',
        help="Select the execution mode of the app (init, edit, upload, test or build).",
        description="For more information on each subcommand, run 'spqr <mode> -h'")
    # The main mode for recipe creation is `spqr build`

    init_parser = subparsers.add_parser(
        'init', help='Generate default configuration files for quick start.')
    build_parser = subparsers.add_parser(
        'build', help='<<< Build a SEM recipe: main mode.',
        description=("Build a SEM recipe from a configuration file and coordinates. "
                     "See `spqr init' command to get templates."))
    upload_parser = subparsers.add_parser(
        'upload', help='Upload a given recipe and/or layout to Recipe Director.')
    test_parser = subparsers.add_parser(
        'test', help='Run the "testing" mode of the app. Meant for developers.',
        description='Refer to app_config.json.')
    edit_parser = subparsers.add_parser(
        'edit', help='Edit a given HSS recipe (experimental).')

    # SPQR Init
    init_parser.add_argument(
        '-c', '--config_file', type=Path,
        help='Path (file or directory) to write a configuration file (JSON).')
    init_parser.add_argument(
        '-x', '--coordinate_file', type=Path,
        help='Path (file or directory) to write a generic coordinate file (genepy format).')

    # SPQR Build
    build_parser.add_argument(
        '-c', '--config', required=True, type=Path,
        help="Path to JSON configuration file containing the recipe parameters.")
    build_parser.add_argument(
        '-r', '--recipe',
        help='Name of the recipe to run, from the JSON configuration file.')
    build_parser.add_argument(
        '-u', '--upload_rcpd', action="store_true",
        help='Send HSS recipe (.csv) and layout to RecipeDirector machine.')
    build_parser.add_argument(
        '-l', '--line_select', required=False, nargs='+', type=str, metavar="RANGE",
        help='Select range(s) of rows to include. Format: -l 50-60 150-160')
    build_parser.add_argument(
        '-m', '--measure', action="store_true",
        help='Write the raw data measured from layout to recipe output directory')

    # SPQR Upload
    upload_parser.add_argument('-r', '--recipe', type=Path, help="Path to recipe to upload.")
    upload_parser.add_argument('-l', '--layout', type=Path, help="Path to layout to upload.")

    # SPQR Test
    test_parser.add_argument(
        '-r', '--recipe', type=str,
        choices=['genepy', 'calibre_rulers', 'opcfield', 'csv', 'json'],
        help='Run the selected recipe type in testing mode.')
    test_parser.add_argument(
        '-a', '--all_recipes', action="store_true",
        help='Run all recipes types in testing mode.')

    # SPQR Edit
    edit_parser.add_argument(
        '-r', '--recipe_file', required=True, type=Path,
        help="Path of the HSS recipe to modify (.csv).")
    edit_parser.add_argument(
        '-c', '--config_file', required=True, type=Path,
        help="Path of the user configuration file to modify (.json).")
    edit_parser.add_argument(
        '-n', '--recipe_name', required=True, type=Path,
        help="Name of the recipe within the configuration file.")

    return parser


def check_recipe(full_config: dict[str, dict], recipe_name: str) -> dict:
    """Verifies that the configuration file and CLI command match in different cases."""
    if len(full_config) == 0:
        raise ValueError("The provided configuration file does not contain any recipe.")
    elif len(full_config) == 1 and recipe_name is None:
        # recipe name is optional if there is only one
        recipe_name = next(iter(full_config.keys()))
    elif len(full_config) > 1 and recipe_name is None:
        logging.warning(
            "More than one recipe found in the configuration file. "
            "Please select one with the -r/--recipe option.")
        sys.exit(1)

    if recipe_name not in full_config:
        logging.error(f'TU QUOQUE FILI !? Recipe {recipe_name} not found in the JSON config file.')
        sys.exit(1)

    return full_config[recipe_name]

# import inquirer
# def cli_list_selection(message: str, choices: list):
#     questions = [
#         inquirer.List('choice',
#                       message=message,
#                       choices=choices,
#                       ),
#     ]
#     answers = inquirer.prompt(questions)
#     return f"You selected: {answers['choice']}"
