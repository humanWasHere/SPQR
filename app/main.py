import pandas as pd
from parser_modules.ssfile_parser import SsfileParser
from measure_modules.measure import Measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator

# ressource definition
genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"  # genepy files  # TODO ask user for path
# TODO variabiliser les chemins de fichiers
excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
layers = ["1.0"]

# TODO
# to make one module a section of this file (ez recognizable parts to run -> maintainability)
# get_eps_data() + write_in_file() to call in hss_creator ?


def run_recipe_creation_w_measure():
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    # # ask user his name
    # user_name = input('What is your unix username ? \n')

    print('1. ssfile parsing')
    # function call with corresponding file as entry
    parser_instance = SsfileParser(genepy_ssfile, is_genepy=True)
    # ssfile_genepy_df = parser_instance.ssfile_to_dataframe()
    ssfile_genepy_df = parser_instance.ssfile_to_dataframe().iloc[:30]
    print('\tssfile parsing done')
    # selection des colonnes d'interet
    INPUT_DF = ssfile_genepy_df[['Name', 'X_coord_Pat', 'Y_coord_Pat']]

    # print('2. measurement')
    # measure_df = measure.sequence_auto(INPUT_DF, layout, layers)  # username=user_name
    # # Index(['Gauge ', ' Layer ', ' Polarity (polygon) ', ' X_dimension(nm) ', ' Y_dimension(nm) ', ' min_dimension(nm)', ' complementary(nm)', ' pitch_of_min_dim(nm)'], dtype='object')
    # # cropped_df = Measure.clean_unknown(last_df.loc[:, ['Gauge ', ' X_dimension(nm) ', ' Y_dimension(nm) ']])
    # print("\tmerging dfs")
    # merged_dfs = pd.merge(ssfile_genepy_df, measure.clean_unknown(measure_df), left_on='Name', right_on='Gauge ')
    # merged_dfs = merged_dfs.drop('Gauge ', axis=1)
    # merged_dfs = merged_dfs.rename(columns={'Name': 'Gauge name'})  # if needed
    # print('\tmeasurement done')

    # this line represents the centralization of parsing to a namming convention
    formated_df = ssfile_genepy_df

    print('2. measurement')
    measure_instance = Measure(formated_df, INPUT_DF, layout, layers)
    output_measure = measure_instance.run_measure()
    print('\tmeasurement done')

    # # in order to ease the time running the app we store the merged df in a file
    # output_measure = "/work/opc/all/users/chanelir/semrc/app/measure_result.temp"
    # merged_dfs.to_csv(output_measure, index=False)

    print('3. <EPS_Data> section creation')
    # création <EPS_Data> section
    # EPS_DataFrame = DataFrameToEPSData(merged_dfs)
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data()
    print('\t<EPS_Data> created')
    # run mapping method call
    print('4. .hss file creation')
    # hss_creation
    runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    # TODO if all methods are run in __init__ add add_mp attribut in __init__ attributes
    runHssCreation.write_in_file(0)
    print('\trecipe created !')


def run_recipe_creation():
    '''this function bypasses the measure for the speed of testing - testing function'''
    # hss_creation
    EPS_DataFrame = DataFrameToEPSData(pd.read_csv(
        "/work/opc/all/users/chanelir/semrc-test/measure_result.temp"))  # TODO must be deleted
    # run mapping method call
    EPS_Data = EPS_DataFrame.get_eps_data()
    runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    runHssCreation.write_in_file(0)


def test_test_recipe_default():
    '''test function for test - MUST BE DELETED'''
    runHssCreation = HssCreator(eps_dataframe=pd.DataFrame())
    runHssCreation.write_in_file(0)


if __name__ == "__main__":
    run_recipe_creation_w_measure()
    # run_recipe_creation()
    # test_test_recipe_default()
