from lxml.etree import XMLSyntaxError

from .data_structure import Block
from .export_hitachi.eps_data import DataFrameToEPSData
from .export_hitachi.hss_creator import HssCreator
from .interfaces.input_checker import UserInputChecker
from .interfaces import recipedirector as rcpd
from .measure.measure import Measure
from .parsers.xml_parser import CalibreXMLParser
from .parsers.ssfile_parser import SSFileParser, OPCfieldReverse

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
    parser = input("Enter a path to your coordinate source :\n")
    layout = user_input.get_secured_user_filepath("Enter a path to your layout :\n")
    layers = user_input.get_secured_user_list_int_float(
        "Enter layer(s) number list (separated by comma + space ', ' each time):\n")
    INPUTS = dict(coord_file=parser, layout=layout, layers=layers, mag=200_000, mp_template="X90M_GATE_PH")
    block = Block(INPUTS['layout'])

    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change to better selection logic (must choose between path or empty but not accept to take both)
    if parser == '':
        # considering retro engineering the opcfield
        # TODO make OPCfieldReverse inputs dynamic ?
        # parser_instance = OPCfieldReverse(origin_x=13357.5, origin_y=17447.5, step_x=15, step_y=15, num_steps_x=24, num_steps_y=66, origin_number=0)  # layer intérêt = 247
        parser_instance = OPCfieldReverse(12888.5, 16507.5, 10, 10, 33, 93)  # layer intérêt = 7.0
        # parser_instance = OPCfieldReverse(origin_x=12895.1, origin_y=17506.4, step_x=10, step_y=10, num_steps_x=39, num_steps_y=97, origin_number=0)  # layer intérêt = 2.0
        rows = (0, 100)
        # rows = None
    else:
        try:
            parser_instance = CalibreXMLParser(INPUTS['coord_file'])
            rows = None
            # data_parsed = parser_instance.parse_data()
        except (XMLSyntaxError, AttributeError):
            parser_instance = SSFileParser(INPUTS['coord_file'], is_genepy=True)
            rows = (60, 70)
            # rows = None
            # data_parsed = parser_instance.parse_data()

    measure_instance = Measure(parser_instance, block, layers, row_range=rows)
    output_measure = measure_instance.run_measure()
    output_measure['magnification'] = INPUTS['mag']  # TODO shouldn't be here - core data ? / like block that would map

    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data(INPUTS['mp_template'])

    mask_layer = int(layers[0].split('.')[0])  # TODO improve
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=mask_layer, layout=block.layout_path, topcell=block.topcell, precision=block.precision, recipe_name="recipe")
    runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(runHssCreation.output_path)
        rcpd.upload_gds(layout)


if __name__ == "__main__":
    run_recipe_creation_w_measure()
