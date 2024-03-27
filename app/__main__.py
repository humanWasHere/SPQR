from parser_modules.parse import CalibreXMLParser
from parser_modules.ssfile_parser import SsfileParser
from measure_modules.measure import Measure
from hss_modules.dataframe_to_eps_data import DataFrameToEPSData
from hss_modules.hss_creator import HssCreator
from connection_modules.shell_commands import ShellCommands

test_genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"
# excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
test_calibre_rulers = "/work/opc/all/users/banger/dev/semchef/examples/calibre_rulers.xml"
test_layout = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"
test_layers = ["1.0"]
genepy_ssfile = ''
layout = ''
layers = ''
MAG = 200_000

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?
# output json format recipe if modification needs to be done afterwards -> in hss creator output json from df or from str ?
# -> reprendre import_json() and json_to_dataframe() from hss_creator.py -> make a function to import
# toggle -> send on sem ? yes or no
# changer parsing and printing en fonction du type d'entrée
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def get_user_inputs():
    # FIXME selection between parsing
    # FIXME create a module outside of main in parser_modules that does the parser splitting/distribution
    # __________ruler calibre__________
    # global calibre_ruler, layout, layers
    # calibre_ruler = input("Enter a (valid) path to your calibre ruler file :\n") or test_calibre_rulers
    # if calibre_ruler == test_calibre_rulers:
    #     print("calibre ruler is set by default")
    # __________genepy ssfile__________
    global genepy_ssfile, layout, layers
    genepy_ssfile = input("Enter a (valid) path to your genepy ssfile (enter to test) :\n") or test_genepy_ssfile
    if genepy_ssfile == test_genepy_ssfile:
        print("ssfile is set by default")
    # __________layout/layers__________
    layout = input("Enter a (valid) path to your layout (enter to test) :\n") or test_layout
    if layout == test_layout:
        print("layout is set by default")
    layers_input = input("Enter a (valid) layer number list (separated with comma + space ', ' each time / enter to test) :\n") or ', '.join(test_layers)
    layers = [layer.strip() for layer in layers_input.split(',')]
    if layers == test_layers:
        print("layers are set by default")


def run_recipe_creation_w_measure():
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # __________ruler calibre__________
    # TODO recipe returns no eps_data ???
    # calibre_ruler_parser_instance = CalibreXMLParser(test_calibre_rulers)
    # data_parsed = calibre_ruler_parser_instance.parse_data()
    # parser_input = 'calibre_ruler'
    # __________genepy ssfile__________
    # FIXME tester recette avant présentation jeudi 28
    ssfile_parser_instance = SsfileParser(genepy_ssfile, is_genepy=True)
    # data_parsed = ssfile_parser_instance.parse_data()
    data_parsed = ssfile_parser_instance.parse_data().iloc[:30]
    parser_input = 'genepy_ssfile'
    # __________following recipe__________
    measure_instance = Measure(data_parsed, layout, layers)
    output_measure = measure_instance.run_measure()
    output_measure['magnification'] = MAG
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    # EPS_Data = EPS_DataFrame.get_eps_data(parser_input)  # can be 'calibre_ruler' or 'genepy_ssfile'
    EPS_Data = EPS_DataFrame.get_eps_data(parser_input)
    runHssCreation = HssCreator(eps_dataframe=EPS_Data)
    runHssCreation.write_in_file()
    shell_command_instance = ShellCommands()
    shell_command_instance.run_scp_command_to_rcpd(runHssCreation.recipe_output_name, runHssCreation.recipe_output_path)


if __name__ == "__main__":
    get_user_inputs()
    run_recipe_creation_w_measure()
