import argparse
import sys
from pathlib import Path

import numpy as np

from .data_structure import Block
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import CheckConfig
from .interfaces import recipedirector as rcpd
from .measure.measure import Measure
from .parsers.json_parser import import_json
from .parsers.parse import ParserSelection, get_parser, OPCFieldReverse


# TODO
# for prod env : should be cd /dist run semrc.exe
# overlap input data with GUI selection
# check if output_dir+recipe_name.(json/csv).exists -> ask user


def cli() -> argparse.ArgumentParser:
    """defines the command lines actions of the soft"""
    parser = argparse.ArgumentParser(prog='spqr', description='-----CLI tool for SEM Recipe Creation-----')
    subparsers = parser.add_subparsers(dest='running_mode',
                                       help='Selects the running mode of the app (start or build). End user should use build.')

    start_parser = subparsers.add_parser('start', help='Runs the "testing" mode of the app. Meant for app developers.')
    start_parser.add_argument('-r', '--recipe_type_selection', required=True,
                              help='Runs the recipe inputted (genepy, calibre_rulers or opcifield) in testing mode. Refer to app_config.json.',
                              choices=['genepy', 'calibre_rulers', 'opcfield'],
                              type=str)

    build_parser = subparsers.add_parser('build', help='Runs the "prod" mode of the app. Meant for end user.')
    build_parser.add_argument('-c', '--user_config', required=True, type=Path,
                              help="Path to user JSON config file containing recipe options.")
    build_parser.add_argument('-r', '--user_recipe',
                              help='Runs the recipe inputted if it is matching one in user_config.json. Refer to this file')
    build_parser.add_argument('-u', '--upload_rcpd', action="store_true",
                              help='Send HSS recipe (.csv) and layout to RecipeDirector machine.')
    build_parser.add_argument('-l', '--line_selection', required=False, nargs=2, type=int, metavar=('START', 'END'),
                              help='Allows user to run a recipe creation with a selected range of lines. Must be written like so : "-l 50 60" where 50 and 60 are included')
    return parser


def manage_app_launch():
    """reads the user command at __main__.py start, then config.json and launches the corresponding command"""
    # TODO if several dict -> several recipe -> run several recipes
    # TODO make a checker of user_config.json before running the recipe
    args = cli().parse_args()
    # Post process args
    if not args.running_mode:
        print("CLI app should be executed as indicated below.\n")
        cli().print_help()
        sys.exit(1)
    if args.line_selection is not None:
        args.line_selection = tuple(args.line_selection)

    if args.running_mode == 'start':
        app_config_file = Path(__file__).resolve().parents[1] / "assets" / "app_config.json"
        app_config = import_json(app_config_file)
        assert app_config != ""  # TODO test it another way
        test_env_config = app_config.get(args.recipe_type_selection)
        config_checker_instance = CheckConfig(test_env_config)
        # config_checker_instance.check_config(check_parser=args.recipe_type_selection != "opcfield")  # checks mandatory values
        config_checker_instance.check_config()
        if args.recipe_type_selection != "calibre_rulers":
            run_recipe_creation_w_measure(test_env_config, line_selection=(100, 110))
        else:
            run_recipe_creation_w_measure(test_env_config, line_selection=(10, 20))
        # TODO for loop to run all test dev recipes with arg -a
    elif args.running_mode == 'build':
        assert args.user_config.exists(), f"Le fichier spécifié n'existe pas: {args.user_config}"
        assert args.user_config.is_file(), f"Le chemin spécifié n'est pas un fichier: {args.user_config}"
        # TODO validate whole JSON
        user_config = import_json(args.user_config)
        if len(user_config) == 0:
            raise ValueError("The provided configuration file does not contain any recipe.")
        if len(user_config) == 1 and args.user_recipe is None:
            # recipe name is optional if there is only one
            args.user_recipe = next(iter(user_config.keys()))
        if len(user_config) > 1 and args.user_recipe is None:
            print("You have more than one recipe in your configuration file. It means you need to select one with the -r attribute.")
            sys.exit(1)
        if args.user_recipe in user_config:
            # print(f'running recipe {args.user_recipe}')
            build_config = user_config.get(args.user_recipe, {})
            config_checker_instance = CheckConfig(build_config)
            config_checker_instance.check_config()
            if isinstance(build_config['step'], list):
                steps = build_config['step']
                for part, step in enumerate(steps):
                    print(f"\ncreating recipe {build_config['recipe_name']} "
                          f"{part+1}/{len(steps)}: {step} from {steps}")
                    copied_config = build_config.copy()
                    copied_config['step'] = step
                    copied_config['recipe_name'] = str(f"{build_config['recipe_name']}_{step}")
                    run_recipe_creation_w_measure(copied_config, args.upload_rcpd, args.line_selection)
            else:
                run_recipe_creation_w_measure(build_config, args.upload_rcpd, args.line_selection)
        else:
            print(f'no recipe {args.user_recipe} has been found in your config file .json.')
            sys.exit(1)


def run_recipe_creation_w_measure(json_conf: dict, upload=False, line_selection=None):
    """this is the real main function which runs the flow with the measure - "prod" function"""
    block = Block(json_conf['layout'])

    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # parser selection
    # parser_selection_instance = ParserSelection(json_conf)
    # selected_parser = parser_selection_instance.run_parsing_selection()
    parser = get_parser(json_conf['parser'])
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
    output_measure = measure_instance.run_measure()

    # renaming of measure points
    if isinstance(selected_parser, OPCFieldReverse):
        cd_space = output_measure["polarity"].str[:2] + output_measure[' min_dimension(nm)'].astype(int).astype(str)
        iso = output_measure[' pitch_of_min_dim(nm)'] == output_measure[' min_dimension(nm)']
        pitch = np.where(iso, "ISO", 'P' + output_measure[' pitch_of_min_dim(nm)'].astype(int).astype(str))
        output_measure.name = cd_space + '_' + pitch + '_' + output_measure.name.astype(str)

    # all recipe's sections creation
    runHssCreation = HssCreator(core_data=output_measure, block=block, json_conf=json_conf,
                                polarity=json_conf.get('polarity', 'clear').lower())
    recipe_path = runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(recipe_path)
        rcpd.upload_gds(json_conf['layout'])
        # TODO if file already exists on remote, check if new file is changed
        print(f"recipe named {json_conf['recipe_name']} should be on RCPD machine !")


if __name__ == "__main__":
    manage_app_launch()
