from parser_modules.parse import CalibreXMLParser
from parser_modules.ssfile_parser import SsfileParser
from xml.etree.ElementTree import ParseError
from measure_modules.measure import Measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator
from app_checkers.get_user_inputs import GetUserInputs
from connection_modules.shell_commands import ShellCommands
from connection_modules import connection


# test_genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"
# excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
# test_calibre_rulers = "/work/opc/all/users/banger/dev/semchef/examples/calibre_rulers.xml"
# test_layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
# test_layers = ["1.0"]
MAG = 200_000

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?
# output json format recipe if modification needs to be done afterwards -> in hss creator output json from df or from str ?
# toggle -> send on sem ? yes or no
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def run_recipe_creation_w_measure():
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    # FIXME class ???
    get_user_path_instance = GetUserInputs()
    parser = get_user_path_instance.get_user_secured_path("Enter a path to your coordinate source :\n")
    layout = get_user_path_instance.get_user_secured_path("Enter a path to your layout :\n")
    layers = get_user_path_instance.get_user_secured_list_int_float("Enter layer(s) number list (separated by comma + space ', ' each time):\n")
    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change selection logic
    # TODO faire des checks de file extension ?
    try:
        parser_instance = CalibreXMLParser(parser)
        data_parsed = parser_instance.parse_data()
        # TODO calibre ruler checker -> verify file extension vs file content
    except ParseError:
        parser_instance = SsfileParser(parser, is_genepy=True)
        data_parsed = parser_instance.parse_data().iloc[60:70]
        # TODO genepy ssfile checker -> verify file extension vs file content
    # TODO pass FileParser instance directly (and optional slice?)
    measure_instance = Measure(data_parsed, layout, layers, unit=parser_instance.unit)
    output_measure = measure_instance.run_measure()
    # TODO add it in core_data instead
    output_measure['magnification'] = MAG  # TODO shouldn't be here -> parse should centralize data after measure here
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data("X90M_GATE_PH")
    topcell = measure_instance.layout_peek("topcell")  # TODO move, optimize
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=layers[0].split(',')[0], layout=layout, topcell=topcell)
    runHssCreation.write_in_file()
    # shell_command_instance = ShellCommands()
    # shell_command_instance.run_scp_command_to_rcpd(runHssCreation.recipe_output_name, runHssCreation.recipe_output_path)
    # connection.upload_csv(runHssCreation.path_output_file)
    # connection.upload_gds(layout)


if __name__ == "__main__":
    run_recipe_creation_w_measure()
