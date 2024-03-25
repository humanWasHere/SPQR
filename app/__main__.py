from parser_modules.parse import CalibreXMLParser
from parser_modules.ssfile_parser import SsfileParser
from measure_modules.measure import Measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator
# from connection_modules.shell_commands import ShellCommands

# renamed __main__.py for coverage lib

genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"
excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
calibre_rulers = "/work/opc/all/users/banger/dev/semchef/examples/calibre_rulers.xml"
layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
layers = ["1.0"]
MAG = 200_000

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?
# output json format recipe if modification needs to be done afterwards -> in hss creator output json from df or from str ?
# -> reprendre import_json() and json_to_dataframe() from hss_creator.py -> make a function to import


def run_recipe_creation_w_measure():
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    print('1. ssfile parsing')
    parser_instance = SsfileParser(genepy_ssfile, is_genepy=True)
    # parser_instance = CalibreXMLParser(calibre_rulers)
    
    # ssfile_genepy_df = parser_instance.parse_data()
    ssfile_genepy_df = parser_instance.parse_data().iloc[:30]
    print('\tssfile parsing done')
    print('2. measurement')
    measure_instance = Measure(ssfile_genepy_df, layout, layers)
    output_measure = measure_instance.run_measure()
    output_measure['magnification'] = MAG
    print('\tmeasurement done\n3. <EPS_Data> section creation')
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data()
    print('\t<EPS_Data> created\n4. .hss file creation')
    runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    runHssCreation.write_in_file()
    print('\trecipe created !')

    # TODO output JSON recipes
    # TODO send recipe to SEM using shell_commands.py
    # TODO get recipe name if we dynamically ask user to name his recipe -> get info in creation -> from hss_creator module


if __name__ == "__main__":
    run_recipe_creation_w_measure()
