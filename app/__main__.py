import argparse
from lxml.etree import XMLSyntaxError
import sys
from pathlib import Path

from .data_structure import Block
from .export_hitachi.eps_data import DataFrameToEPSData
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import CheckConfig
from .interfaces.recipedirector import rpcd
from .measure.measure import Measure
from .parsers.parse import OPCfieldReverse
from .parsers.json_parser import import_json
from .parsers.xml_parser import CalibreXMLParser
from .parsers.ssfile_parser import SSFileParser


# TODO
# overlap input data with GUI selection
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more
# check if output_dir+recipe_name.(json/csv).exists -> ask user


def manage_app_launch():
    '''reads the user command at __main__.py start, then config.json and launches the corresponding command'''
    parser = argparse.ArgumentParser(description='Manage application launch commands.')
    parser.add_argument('command', help='The command to execute (start or build).')
    parser.add_argument('subcommand', nargs='?', help='The subcommand to execute (genepy, calibre_ruler, opcfield).')
    args = parser.parse_args()

    app_config_file = Path(__file__).resolve().parent / "app_config.json"
    app_config = import_json(app_config_file)

    command_name = args.command
    subcommand_name = args.subcommand
    command = app_config.get('scripts', {}).get(command_name)
    if command:
        if command_name == "start" and subcommand_name:
            if subcommand_name in ["genepy", "calibre_rulers", "opcfield"]:
                test_env_config = app_config.get(subcommand_name, {})
                run_recipe_creation_w_measure(test_env_config)
            else:
                print(f"Le sous-commande '{subcommand_name}' n'est pas définie pour la commande 'start'.")
                sys.exit(1)
        elif command_name == "build":
            user_config_file = Path(__file__).resolve().parent / "user_config.json"
            user_config = import_json(user_config_file)
            build_env_config = user_config.get("testcase_elodie", {})
            config_checker_instance = CheckConfig(build_env_config)
            config_checker_instance.check_config()
            if isinstance(build_env_config['step'], list):
                recipe_part = 0
                for step in build_env_config['step']:
                    copied_build_env_config = {key: value for key, value in build_env_config.items()}
                    recipe_part += 1
                    print(f"\ncreating recipe{recipe_part}/{len(build_env_config['step'])} : {step} pour {copied_build_env_config['step']}")
                    copied_build_env_config['step'] = step
                    copied_build_env_config['recipe_name'] = str(f"{build_env_config['recipe_name']}_p{recipe_part}")
                    run_recipe_creation_w_measure(copied_build_env_config)
            else:
                run_recipe_creation_w_measure(build_env_config)
    else:
        print(f"La commande '{command_name}' n'est pas définie dans app_config.json.")
        sys.exit(1)


def run_recipe_creation_w_measure(json_conf: dict, upload=False):
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    block = Block(json_conf['layout'])
    # assert set(json_conf.keys()).issubset({"recipe_name", "parser", "layout", "layers", "magnification", "mp_template", "step", "opcfield_x", "opcfield_y", "step_x", "step_y", "num_step_x", "num_step_y"})

    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change to better selection logic (must choose between path or empty but not accept to take both)
    if json_conf['parser'] == "":
        # parser_instance = OPCfieldReverse(origin_x=13357.5, origin_y=17447.5, step_x=15, step_y=15, num_steps_x=24, num_steps_y=66, origin_number=0)  # layer intérêt = 247
        # parser_instance = OPCfieldReverse(12888.5, 16507.5, 10, 10, 33, 93)  # layer intérêt = 7.0
        # parser_instance = OPCfieldReverse(origin_x=12895.1, origin_y=17506.4, step_x=10, step_y=10, num_steps_x=39, num_steps_y=97, origin_number=0)  # layer intérêt = 2.0
        parser_instance = OPCfieldReverse(json_conf['opcfield_x'], json_conf['opcfield_y'], json_conf['step_x'],
                                          json_conf['step_y'], json_conf['num_step_x'],
                                          json_conf['num_step_y'])
        rows = None  # (0, 100)
    else:
        try:
            parser_instance = CalibreXMLParser(json_conf['parser'])
            rows = None  # or tuple
        except (XMLSyntaxError, AttributeError):
            parser_instance = SSFileParser(json_conf['parser'], is_genepy=True)
            # /!\ only manages genepy ssfile at the moment
            rows = (60, 70)  # (60, 70) / None

    measure_instance = Measure(parser_instance, block, json_conf['layers'], row_range=rows)
    output_measure = measure_instance.run_measure()

    EPS_DataFrame = DataFrameToEPSData(output_measure, json_conf)
    EPS_Data = EPS_DataFrame.get_eps_data()

    # TODO round number to unit ?
    mask_layer = int(json_conf['layers'][0].split('.')[0])
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=mask_layer, block=block, recipe_name=json_conf['recipe_name'],
                                output_dir=json_conf['output_dir'])
    runHssCreation.write_in_file()
    if upload:
        qcg_5_k_instance = rpcd(runHssCreation.recipe_output_dir)
        qcg_5_k_instance.upload_csv()
        qcg_5_k_instance.upload_gds()


if __name__ == "__main__":
    manage_app_launch()
