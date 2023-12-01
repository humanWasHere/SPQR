import pandas as pd
from measure_modules.measure import measure
from parser_modules.ssfile_parser import ssfileParser
# from parser_modules.excel_parser import excelParser

# ressource definition
genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"  # genepy files
genepy = [genepy_ssfile]
excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
layers = ["1.0"]

if __name__ == "__main__":
    parser_instance = ssfileParser(genepy_ssfile, is_genepy=True)  # function call with corresponding file as entry
    ssfile_genepy_df = parser_instance.ssfile_to_dataframe()
    # selection des colonnes d'interet
    data = ssfile_genepy_df[['Name', 'X_coord_Pat', 'Y_coord_Pat']]

    # or

    # parser_instance = excelParser(excel_file)
    # excel_df = parser_instance.excel_to_dataframe()
    # data = excel_df[['Name', 'X_coord_Pat', 'Y_coord_Pat']]

    INPUT_DF = pd.DataFrame(data)

    last_df = measure.sequence_auto(INPUT_DF, layout, layers)
    # Index(['Gauge ', ' Layer ', ' Polarity (polygon) ', ' X_dimension(nm) ', ' Y_dimension(nm) ', ' min_dimension(nm)',
    # ' complementary(nm)', ' pitch_of_min_dim(nm)'], dtype='object')
    cropped_df = measure.clean_unknown(last_df.loc[:, ['Gauge ', ' X_dimension(nm) ', ' Y_dimension(nm) ']])
    merged_dfs = pd.merge(ssfile_genepy_df, cropped_df, left_on='Name', right_on='Gauge ')
    merged_dfs = merged_dfs.drop('Gauge ', axis=1)
    # merged_dfs = merged_dfs.rename(columns={'Name': 'Gauge name'})  # if needed
    # print(INPUT_DF)
    # print(cropped_df)
    print(merged_dfs)
    # merged_dfs.to_csv(path_or_buf="/work/opc/all/users/chanelir/semrc-outputs/csv_output.csv")
