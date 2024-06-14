import argparse
import sys
from pathlib import Path

from .data_structure import Block
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import CheckConfig
from .interfaces import recipedirector as rcpd
from .measure.measure import Measure
from .parsers.json_parser import import_json
from .parsers.parse import ParserSelection


# TODO
# for prod env : should be cd /dist run semrc.exe
# overlap input data with GUI selection
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more
# check if output_dir+recipe_name.(json/csv).exists -> ask user

def cli():
    """defines the command lines actions of the soft"""
    parser = argparse.ArgumentParser(prog='SEM Recipe Creator', description='-----CLI tool for SEM Recipe Creation-----')
    subparsers = parser.add_subparsers(dest='running_mode',
                                       help='Selects the running mode of the app (start or build). End user should use build.')

    start_parser = subparsers.add_parser('start', help='Runs the "testing" mode of the app. Meant for app developers.')
    start_parser.add_argument('-r', '--recipe_type_selection', required=True,
                              help='Runs the recipe inputted (genepy, calibre_rulers or opcifield) in testing mode. Refer to app_config.json.',
                              choices=['genepy', 'calibre_rulers', 'opcfield'],
                              type=str)

    build_parser = subparsers.add_parser('build', help='Runs the "prod" mode of the app. Meant for end user.')
    build_parser.add_argument('-ur', '--user_recipe', required=True,
                              help='Runs the recipe inputted if it is matching one in user_config.json. Refer to this file',
                              type=str)
    build_parser.add_argument('-rd', '--recipe_director', required=False,
                              help='Sends recipe (in .csv) and layout on corresponding RCPD machines. Must be "True" or "False".',
                              choices=[True, False],
                              type=bool)
    build_parser.add_argument('-l', '--line_selection', required=False,
                              help='Allows user to run a recipe creation with a selected range of lines. Must be written like so : "-l 50 60"',
                              nargs='+',
                              type=int)

    args = parser.parse_args()

    if not vars(args).get('running_mode'):
        print("CLI app should be executed as indicated below.\n")
        parser.print_help()
        sys.exit(1)

    return args


def manage_app_launch():
    '''reads the user command at __main__.py start, then config.json and launches the corresponding command'''
    # TODO if several dict -> several recipe -> run several recipes
    # TODO make a checker of user_config.json before running the recipe
    args = cli()
    if args.running_mode == 'start':
        app_config_file = Path(__file__).resolve().parent / "app_config.json"
        app_config = import_json(app_config_file)
        assert app_config != ""  # test it another way
        test_env_config = app_config.get(args.recipe_type_selection)
        config_checker_instance = CheckConfig(test_env_config)
        # config_checker_instance.check_config(check_parser=args.recipe_type_selection != "opcfield")  # checks mandatory values
        config_checker_instance.check_config()
        run_recipe_creation_w_measure(test_env_config)
    elif args.running_mode == 'build':
        user_config_file = Path(__file__).resolve().parent / "user_config.json"
        user_config = import_json(user_config_file)
        if args.user_recipe in user_config:
            # print(f'running recipe {args.user_recipe}')
            build_env_config = user_config.get(args.user_recipe, {})
            config_checker_instance = CheckConfig(build_env_config)
            config_checker_instance.check_config()
            if isinstance(build_env_config['step'], list):
                recipe_part = 0
                for step in build_env_config['step']:
                    copied_build_env_config = {key: value for key, value in build_env_config.items()}
                    recipe_part += 1
                    print(f"\ncreating recipe {copied_build_env_config['recipe_name']}{recipe_part}/{len(build_env_config['step'])} : {step} pour {copied_build_env_config['step']}")
                    copied_build_env_config['step'] = step
                    copied_build_env_config['recipe_name'] = str(f"{build_env_config['recipe_name']}_p{recipe_part}")
                    run_recipe_creation_w_measure(copied_build_env_config, args.recipe_director, tuple(args.line_selection) if args.line_selection is not None else None)
            else:
                run_recipe_creation_w_measure(build_env_config, args.recipe_director, tuple(args.line_selection) if args.line_selection is not None else None)
        else:
            print(f'no recipe {args.user_recipe} has been found in user_config.json.')
            sys.exit(1)


def run_recipe_creation_w_measure(json_conf: dict, upload=False, line_selection=None):
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    block = Block(json_conf['layout'])
    # assert set(json_conf.keys()).issubset({"recipe_name", "parser", "layout", "layers", "magnification", "mp_template", "step", "opcfield_x", "opcfield_y", "step_x", "step_y", "num_step_x", "num_step_y"})

    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # parser selection
    parser_selection_instance = ParserSelection(json_conf)
    selected_parser = parser_selection_instance.run_parsing_selection()

    # measurement
    measure_instance = Measure(selected_parser, block, json_conf['layers'], row_range=line_selection)
    output_measure = measure_instance.run_measure()
    # all recipe's sections creation
    runHssCreation = HssCreator(core_data=output_measure, block=block, json_conf=json_conf)
    recipe_path = runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(recipe_path)
        rcpd.upload_gds(json_conf['layout'])
        print('recipe should be on RCPD machine !')


if __name__ == "__main__":
    manage_app_launch()
