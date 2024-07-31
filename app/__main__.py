import argparse
import logging
import sys
from pathlib import Path

import numpy as np

from .interfaces.logger import logger_init
import logging

logger_init()

from .data_structure import Block
from .export_hitachi.hss_creator import HssCreator
from .interfaces import recipedirector as rcpd
from .interfaces.input_checker import get_config_checker
from .measure.measure import Measure
from .parsers import FileParser, get_parser, OPCFieldReverse
from .parsers.json_parser import import_json


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


logger = logging.getLogger(__name__)


def cli() -> argparse.ArgumentParser:
    """defines the command lines actions of the soft"""
    parser = argparse.ArgumentParser(prog='spqr',
                                     description='----- CLI tool for SEM Recipe Creation -----')
    subparsers = parser.add_subparsers(
        dest='running_mode',
        help='Selects the running mode of the app (start or build). End user should use build.')

    start_parser = subparsers.add_parser(
        'start', help='Runs the "testing" mode of the app. Meant for app developers.')
    start_parser.add_argument('-r', '--recipe', required=True,
                              help='Runs the recipe inputted (genepy, calibre_rulers or opcfield) in testing mode. Refer to app_config.json.',
                              choices=['genepy', 'calibre_rulers', 'opcfield', 'csv', 'json'],
                              type=str)

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
    return parser


def build_mode(args: argparse.Namespace) -> None:
    logger.info('app running in prod mode')
    if not args.user_config.exists() or not args.user_config.is_file():
        raise ValueError(f'Path does not exist or is not a file: {args.user_config}')
    if args.user_config.stat().st_size == 0:
        raise ValueError(f'File is empty: {args.user_config}')

    # TODO validate whole JSON
    user_config = import_json(args.user_config)

    # Recipe selection
    if len(user_config) == 0:
        raise ValueError("The provided configuration file does not contain any recipe.")
    elif len(user_config) == 1 and args.user_recipe is None:
        # recipe name is optional if there is only one
        args.user_recipe = next(iter(user_config.keys()))
    elif len(user_config) > 1 and args.user_recipe is None:
        logger.warning("More than one recipe found in the configuration file. Please select one with the -r option.")
        sys.exit(1)
    if args.user_recipe not in user_config:
        logger.error(f'TU QUOQUE FILI !? Recipe {args.user_recipe} not found in the JSON config file.')
        sys.exit(1)

    # print(f'running recipe {args.user_recipe}')
    build_config = user_config.get(args.user_recipe, {})
    get_config_checker(build_config)  # TODO use return value

    if isinstance(build_config['step'], list):
        steps = build_config['step']
        for part, step in enumerate(steps):
            logger.info(f"recipe {build_config['recipe_name']}"
                        f"{part+1}/{len(steps)}: {step} from {steps}")
            copied_config = build_config.copy()
            copied_config['step'] = step
            copied_config['recipe_name'] = str(f"{build_config['recipe_name']}_{step}")
            create_recipe(copied_config, args.upload_rcpd, parse_intervals(args.line_selection), args.mesurement_file)
    else:
        create_recipe(build_config, args.upload_rcpd, parse_intervals(args.line_selection), args.mesurement_file)


def start_mode(args: argparse.Namespace) -> None:
    logger.info('app running in dev mode')
    app_config_file = Path(__file__).resolve().parents[1] / "assets" / "app_config.json"
    app_config = import_json(app_config_file)
    if not app_config:
        raise ValueError(f"File {app_config_file.name} does not exist or is empty.")

    test_env_config = app_config.get(args.recipe)
    get_config_checker(test_env_config)

    if args.recipe == "calibre_rulers":
        create_recipe(test_env_config, line_selection=[[10, 20]])
    else:
        create_recipe(test_env_config, line_selection=[[100, 110]])
    # TODO for loop to run all test dev recipes with arg -a
    # Draft auto mode (override args and use build)
    # build_mode(cli().parse_args(
    #     ['build', '-c', str(app_config_file), '-r', 'calibre_rulers', '-l', '10-20']))


def manage_app_launch():
    """Read the command line and user config.json and launches the corresponding command"""
    # TODO if several dict -> several recipe -> run several recipes
    # TODO make a checker of user_config.json before running the recipe
    try:
        args = cli().parse_args()
    except SystemExit as e:
        logger.error("Argument parsing failed. Exiting.")
        sys.exit(e.code)

    # Post process args
    if not args.running_mode:
        logger.warning("CLI app arguments should be executed as indicated in the helper below.")
        cli().print_help()
        sys.exit(1)
    # if args.line_selection is not None:
    #     args.line_selection = tuple(args.line_selection)
    try:
        if args.running_mode == 'start':
            start_mode(args)
        elif args.running_mode == 'build':
            build_mode(args)
    except KeyboardInterrupt:
        logger.error('Interrupted by user')
    except Exception as e:
        logger.exception(f'{e.__class__.__name__}')


def create_recipe(json_conf: dict, upload=False, line_selection=None, output_measurement=False):
    """this is the real main function which runs the flow with the measure - "prod" function"""
    block = Block(json_conf['layout'])

    logger.info(f"### CREATING RECIPE ### : {json_conf['recipe_name']}")
    # Parser selection
    parser = get_parser(json_conf['parser'])
    if parser is None:
        raise ValueError("Your coordinate source may not be in a valid format")
    logger.info(f'parser is {parser}')
    selected_parser: FileParser | OPCFieldReverse
    if issubclass(parser, OPCFieldReverse):
        selected_parser = parser(
            json_conf['origin_x_y'][0], json_conf['origin_x_y'][1],
            json_conf['step_x_y'][0], json_conf['step_x_y'][1],
            json_conf['n_rows_cols'][0], json_conf['n_rows_cols'][1],
            json_conf['ap1_offset'][0], json_conf['ap1_offset'][1])
    else:
        selected_parser = parser(json_conf['parser'])

    # measurement
    measure_instance = Measure(selected_parser, block, json_conf['layers'],
                               json_conf.get('translation'), row_range=line_selection)
    output_measure = measure_instance.run_measure(output_dir=json_conf['output_dir'] if output_measurement else None,
                                                  recipe_name=json_conf['recipe_name'] if output_measurement else None)

    # renaming of measure points
    if isinstance(selected_parser, OPCFieldReverse):
        cd_space = (output_measure["polarity"].str[:2]
                    + output_measure[' min_dimension(nm)'].astype(float).astype(int).astype(str))
        iso = output_measure[' pitch_of_min_dim(nm)'] == output_measure[' min_dimension(nm)']
        pitch = np.where(iso, "ISO", 'P' + output_measure[' pitch_of_min_dim(nm)']
                         .replace('Pitch non symetrical', 0).astype(float).astype(int).astype(str))
        output_measure.name = cd_space + '_' + pitch + '_' + output_measure.name.astype(str)

    # all recipe's sections creation
    runHssCreation = HssCreator(core_data=output_measure, block=block, json_conf=json_conf,
                                polarity=json_conf.get('polarity', 'clear').lower())
    recipe_path = runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(recipe_path)
        rcpd.upload_gds(json_conf['layout'])
        # TODO if file already exists on remote, check if new file is changed
        logger.info(f"recipe named {json_conf['recipe_name']} should be on RCPD machine!")
    logger.info("### END RECIPE CREATION ###")


if __name__ == "__main__":
    manage_app_launch()
