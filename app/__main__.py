from parser_modules.parse import CalibreXMLParser
from parser_modules.ssfile_parser import SsfileParser
from xml.etree.ElementTree import ParseError
from measure_modules.measure import Measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator
from app_checkers.get_user_inputs import GetUserInputs
from connection_modules.shell_commands import ShellCommands
from connection_modules import connection


test_genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"
# excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
test_calibre_rulers = "/work/opc/all/users/banger/dev/semchef/examples/calibre_rulers.xml"
test_layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
test_layers = ["1.0"]
MAG = 200_000

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?
# output json format recipe if modification needs to be done afterwards -> in hss creator output json from df or from str ?
# -> reprendre import_json() and json_to_dataframe() from hss_creator.py -> make a function to import
# toggle -> send on sem ? yes or no
# changer parsing and printing en fonction du type d'entrée
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def run_recipe_creation_w_measure():
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    # FIXME class ???
    get_user_path_instance = GetUserInputs()
    get_user_path_instance.get_user_inputs()
    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change selection logic
    try:
        parser_instance = CalibreXMLParser(get_user_path_instance.parser)
        data_parsed = parser_instance.parse_data()
    except ParseError:
        parser_instance = SsfileParser(get_user_path_instance.parser, is_genepy=True)
        data_parsed = parser_instance.parse_data().iloc[60:70]

    # __________following recipe__________
    # TODO pass FileParser instance directly (and optional slice?)
    measure_instance = Measure(data_parsed, get_user_path_instance.layout, get_user_path_instance.layers, unit=parser_instance.unit)
    output_measure = measure_instance.run_measure()
    output_measure['magnification'] = MAG  # TODO shouldn't be here -> parse should centralize data after measure here
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data("X90M_GATE_PH")
    topcell = measure_instance.layout_peek("topcell")  # TODO move, optimize
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layer=get_user_path_instance.layers[0].split('.')[0], layout=get_user_path_instance.layout, topcell=topcell)
    runHssCreation.write_in_file()
    # shell_command_instance = ShellCommands()
    # shell_command_instance.run_scp_command_to_rcpd(runHssCreation.recipe_output_name, runHssCreation.recipe_output_path)
    print(runHssCreation.path_output_file)
    # connection.upload_csv(runHssCreation.path_output_file)
    # connection.upload_gds(layout)


if __name__ == "__main__":
    run_recipe_creation_w_measure()
