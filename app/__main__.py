# from xml.etree.ElementTree import ParseError
from lxml.etree import XMLSyntaxError

from .data_structure import Block
from .export_hitachi.eps_data import DataFrameToEPSData
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import UserInputChecker
from .interfaces import recipedirector as rcpd
from .measure.measure import Measure
from .parsers.xml_parser import CalibreXMLParser
from .parsers.ssfile_parser import SSFileParser

TESTCASE_GENEPY = dict(
    coord_file="/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt",
    layout="/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
    layers=["1.0"],
    mag=200_000,
    mp_template="X90M_GATE_PH",
    step="PH"
)

# test_calibre_rulers = "/work/opc/all/users/banger/dev/semchef/examples/calibre_rulers.xml"

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?
# output json format recipe if modification needs to be done afterwards
#       -> in hss creator output json from df or from str ?
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def run_recipe_creation_w_measure(upload=False):
    '''this is the real main function which runs the flow with the measure - "prod" function'''
    user_input = UserInputChecker()
    parser = user_input.get_secured_user_filepath("Enter a path to your coordinate source :\n")
    layout = user_input.get_secured_user_filepath("Enter a path to your layout :\n")
    layers = user_input.get_secured_user_list_int_float(
        "Enter layer(s) number list (separated by comma + space ', ' each time):\n")
    INPUTS = dict(coord_file=parser, layout=layout, layers=layers, mag=200_000, mp_template="X90M_GATE_PH")
    block = Block(INPUTS['layout'])

    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change selection logic
    try:
        parser_instance = CalibreXMLParser(INPUTS['coord_file'])
        rows = None
        # data_parsed = parser_instance.parse_data()
    except (XMLSyntaxError, AttributeError):
        parser_instance = SSFileParser(INPUTS['coord_file'], is_genepy=True)
        rows = (60, 70)
        # data_parsed = parser_instance.parse_data()

    measure_instance = Measure(parser_instance, block, layers, row_range=rows)
    output_measure = measure_instance.run_measure()
    output_measure['magnification'] = INPUTS['mag']  # TODO shouldn't be here - core data ?

    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data(INPUTS['mp_template'])

    mask_layer = int(layers[0].split('.')[0])  # TODO improve
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=mask_layer, layout=block.layout_path, topcell=block.topcell, precision=block.precision)
    # runHssCreation = HssCreator(eps_dataframe=EPS_Data, block=block, layers=mask_layer)
    runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(runHssCreation.output_path)
        rcpd.upload_gds(layout)


if __name__ == "__main__":
    run_recipe_creation_w_measure()
