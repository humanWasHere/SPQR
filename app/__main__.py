from lxml.etree import XMLSyntaxError
import json
import sys
from pathlib import Path

from .data_structure import Block
from .export_hitachi.eps_data import DataFrameToEPSData
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import UserInputChecker, Config
from .interfaces import recipedirector as rcpd
from .measure.measure import Measure
from .parsers.xml_parser import CalibreXMLParser
from .parsers.ssfile_parser import SSFileParser, OPCfieldReverse


# TODO
# overlap input data with GUI selection
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def manage_app_launch():
    '''reads the user command at __main__.py start, then config.json and launches the corresponding command'''
    app_config_file = Path(__file__).resolve().parent / "app_config.json"
    app_config = json.loads(app_config_file.read_text())
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
            user_config = json.loads(user_config.read_text())
            build_env_config = user_config.get("build_env", {})
            config_checker_instance = Config(build_env_config)
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
    # user_input = UserInputChecker()
    # parser = input("Enter a path to your coordinate source :\n")
    # layout = user_input.get_secured_user_filepath("Enter a path to your layout :\n")
    # layers = user_input.get_secured_user_list_int_float(
    #     "Enter layer(s) number list (separated by comma + space ', ' each time):\n")
    # INPUTS = dict(coord_file=parser, layout=layout, layers=layers,
    #               mag=200_000, mp_template="X90M_GATE_PH")
    # block = Block(INPUTS['layout'])
    block = Block(json_conf['layout'])

    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change to better selection logic (must choose between path or empty but not accept to take both)
    # if parser == '':
    if json_conf['parser'] == "":
        # considering retro engineering the opcfield
        # TODO make OPCfieldReverse inputs dynamic ?
        # parser_instance = OPCfieldReverse(origin_x=13357.5, origin_y=17447.5, step_x=15, step_y=15, num_steps_x=24,
        #                                   num_steps_y=66, origin_number=0)  # layer intérêt = 247
        # parser_instance = OPCfieldReverse(12888.5, 16507.5, 10, 10, 33, 93)  # layer intérêt = 7.0
        # parser_instance = OPCfieldReverse(origin_x=12895.1, origin_y=17506.4, step_x=10, step_y=10, num_steps_x=39,
        #                                   num_steps_y=97, origin_number=0)  # layer intérêt = 2.0
        parser_instance = OPCfieldReverse(json_conf['opcfield_x'], json_conf['opcfield_y'], json_conf['step_x'],
                                          json_conf['step_y'], json_conf['num_step_x'],
                                          json_conf['num_step_y'])  # layer intérêt = 7.0
        rows = (0, 100)
        # rows = None
    else:
        try:
            # parser_instance = CalibreXMLParser(INPUTS['coord_file'])
            parser_instance = CalibreXMLParser(json_conf['parser'])
            rows = None  # or tuple
            # data_parsed = parser_instance.parse_data()
        except (XMLSyntaxError, AttributeError):
            # parser_instance = SSFileParser(INPUTS['coord_file'], is_genepy=True)
            parser_instance = SSFileParser(json_conf['parser'], is_genepy=True)
            # /!\ only manages genepy ssfile at the moment
            rows = (60, 70)  # or None
            # data_parsed = parser_instance.parse_data()

    # measure_instance = Measure(parser_instance, block, layers, row_range=rows)
    measure_instance = Measure(parser_instance, block, json_conf['layers'], row_range=rows)
    output_measure = measure_instance.run_measure()
    # output_measure['magnification'] = INPUTS['mag']  # TODO shouldn't be here - core data ?
    output_measure['magnification'] = json_conf['magnification']

    EPS_DataFrame = DataFrameToEPSData(output_measure)
    # EPS_Data = EPS_DataFrame.get_eps_data(INPUTS['mp_template'])
    EPS_Data = EPS_DataFrame.get_eps_data(json_conf['mp_template'])

    # mask_layer = int(layers[0].split('.')[0])  # TODO improve
    mask_layer = int(json_conf['layers'][0].split('.')[0])
    # runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=mask_layer, recipe_name="recipe")
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=mask_layer, block=block, recipe_name=json_conf['recipe_name'])
    runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(runHssCreation.output_path)
        # rcpd.upload_gds(layout)
        rcpd.upload_gds()


if __name__ == "__main__":
    manage_app_launch()
    # run_recipe_creation_w_measure()
