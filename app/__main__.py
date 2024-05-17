from lxml.etree import XMLSyntaxError
import sys
from pathlib import Path

from .data_structure import Block
from .export_hitachi.eps_data import DataFrameToEPSData
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import UserInputChecker, CheckConfig
from .interfaces.recipedirector import rpcd
from .measure.measure import Measure
from .parsers.json_parser import import_json
from .parsers.xml_parser import CalibreXMLParser
from .parsers.ssfile_parser import SSFileParser, OPCfieldReverse


# TODO
# overlap input data with GUI selection
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def manage_app_launch():
    '''reads the user command at __main__.py start, then config.json and launches the corresponding command'''
    app_config_file = Path(__file__).resolve().parent / "app_config.json"
    app_config = import_json(app_config_file)
    try:
        command_name = sys.argv[1]
    except IndexError:
        print("Veuillez spécifier une commande à exécuter.")
        sys.exit(1)
    # /!\ should not accept second input for type of launch -> security issue
    # must have 1 test conf and 1 prod conf
    # conf file should accept only one prodcase
    command = app_config.get('scripts', {}).get(command_name)
    if command:
        if command_name == "start":
            test_env_config = app_config.get('test_env_genepy', {})
            run_recipe_creation_w_measure(test_env_config)
        elif command_name == "build":
            user_config = Path(__file__).resolve().parent / "user_config.json"
            user_config = import_json(user_config)
            build_env_config = user_config.get("build_env", {})
            config_checker_instance = CheckConfig(build_env_config)
            config_checker_instance.check_config()
            # if config_type == "export":
            #     verif_build_launch = input("Are you sure you want to export your recipe ? (Y/N)")
            #     if verif_build_launch.upper() == "Y":
            #         # run_recipe_creation_w_measure(build_env_config, upload=True)
            #         print("we send the recipe")
            #     else:
            #         print("build has been canceled")
            # else:
            #     run_recipe_creation_w_measure(build_env_config)
            run_recipe_creation_w_measure(build_env_config)
    else:
        print(f"La commande '{command_name}' n'est pas définie dans conf.json.")


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
                                          json_conf['num_step_y'])  # layer intérêt = 7.0
        rows = None  # (0, 100)
    else:
        try:
            parser_instance = CalibreXMLParser(json_conf['parser'])
            rows = None  # or tuple
        except (XMLSyntaxError, AttributeError):
            parser_instance = SSFileParser(json_conf['parser'], is_genepy=True)
            # /!\ only manages genepy ssfile at the moment
            rows = None  # (60, 70)

    measure_instance = Measure(parser_instance, block, json_conf['layers'], row_range=rows)
    output_measure = measure_instance.run_measure()
    output_measure['magnification'] = json_conf['magnification']  # TODO shouldn't be here - core data ?

    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data(json_conf['mp_template'])
    # round number to unit ?
    mask_layer = int(json_conf['layers'][0].split('.')[0])
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=mask_layer, block=block, recipe_name=json_conf['recipe_name'])
    runHssCreation.write_in_file()
    if upload:
        qcg_5_k_instance = rpcd(runHssCreation.recipe_output_dir)
        qcg_5_k_instance.upload_csv()
        qcg_5_k_instance.upload_gds()


if __name__ == "__main__":
    manage_app_launch()
    # run_recipe_creation_w_measure()
