import pandas as pd
from parser_modules.ssfile_parser import ssfileParser
# from parser_modules.excel_parser import excelParser
from measure_modules.measure import measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator
# from hss_modules.hss_modificator import RecipeModificator

# ressource definition
genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"  # genepy files
# liste contenant l'information de classification des ssfile. Ici les fichiers genepy
# afin de savoir quel traitement appliquer avec le bon type de parser avec la data d'entée
# TODO récupérer l'info autrement / variabiliser/user_input pour la récupération des chemins de fichiers au données
genepy = [genepy_ssfile]
excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
layers = ["1.0"]

if __name__ == "__main__":
    # # ask user his name
    # user_name = input('What is your unix username ? \n')

    print('1. ssfile parsing')
    # function call with corresponding file as entry
    parser_instance = ssfileParser(genepy_ssfile, is_genepy=True)
    # ssfile_genepy_df = parser_instance.ssfile_to_dataframe()
    ssfile_genepy_df = parser_instance.ssfile_to_dataframe().iloc[:50]
    print('\t ssfile parsing done')
    # selection des colonnes d'interet
    data = ssfile_genepy_df[['Name', 'X_coord_Pat', 'Y_coord_Pat']]

    INPUT_DF = data

    print('2. measurement')
    measure_df = measure.sequence_auto(INPUT_DF, layout, layers)  # username=user_name
    # Index(['Gauge ', ' Layer ', ' Polarity (polygon) ', ' X_dimension(nm) ', ' Y_dimension(nm) ', ' min_dimension(nm)', ' complementary(nm)', ' pitch_of_min_dim(nm)'], dtype='object')
    # cropped_df = measure.clean_unknown(last_df.loc[:, ['Gauge ', ' X_dimension(nm) ', ' Y_dimension(nm) ']])
    merged_dfs = pd.merge(ssfile_genepy_df, measure.clean_unknown(measure_df), left_on='Name', right_on='Gauge ')
    merged_dfs = merged_dfs.drop('Gauge ', axis=1)
    merged_dfs = merged_dfs.rename(columns={'Name': 'Gauge name'})  # if needed
    print('\t measurement done')

    # # in order to ease the time running the app we store the merged df in a file
    # output_measure = "/work/opc/all/users/chanelir/semrc/app/measure_result.temp"
    # merged_dfs.to_csv(output_measure, index=False)

    print('3. <EPS_Data> section creation')
    # création <EPS_Data> section
    EPS_DataFrame = DataFrameToEPSData(merged_dfs)
    EPS_Data = EPS_DataFrame.get_eps_data()
    print('\t <EPS_Data> created')
    # run mapping method call
    print('4. .hss file creation')
    # hss_creation
    runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    runHssCreation.write_in_file(0)
    print('\t recipe created !')

    # hss_creation
    # EPS_DataFrame = DataFrameToEPSData(pd.read_csv(
    #     "/work/opc/all/users/chanelir/semrc-test/measure_result.temp"))
    # # run mapping method call
    # EPS_Data = EPS_DataFrame.get_eps_data()
    # runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    # runHssCreation.write_in_file(3)
