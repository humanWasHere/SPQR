import pandas as pd
from parser_modules.ssfile_parser import SsfileParser
from measure_modules.measure import Measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator

genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"
excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
layers = ["1.0"]

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?


def run_recipe_creation_w_measure():
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    print('1. ssfile parsing')
    parser_instance = SsfileParser(genepy_ssfile, is_genepy=True)
    
    # ssfile_genepy_df = parser_instance.ssfile_to_dataframe()
    ssfile_genepy_df = parser_instance.parse_data().iloc[:30]
    print('\tssfile parsing done')

    print('2. measurement')
    measure_instance = Measure(ssfile_genepy_df, layout, layers)
    output_measure = measure_instance.run_measure()
    print('\tmeasurement done\n3. <EPS_Data> section creation')
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data()
    print('\t<EPS_Data> created\n4. .hss file creation')
    runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    runHssCreation.write_in_file(0)
    print('\trecipe created !')


if __name__ == "__main__":
    run_recipe_creation_w_measure()
