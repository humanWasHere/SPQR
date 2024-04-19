from xml.etree.ElementTree import ParseError
from .parsers.xml_parser import CalibreXMLParser
from .parsers.ssfile_parser import SsfileParser
from .measure.measure import Measure
from .export_hitachi.eps_data import DataFrameToEPSData
from .export_hitachi.hss_creator import HssCreator
from .interfaces.get_user_inputs import GetUserInputs
from .interfaces import recipedirector as rcpd
from .core_block.block_dataclass import Block

TESTCASE_GENEPY = dict(
    file="/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt",
    layout="/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
    layers=["1.0"],
    mag=200_000,
    mp_template="X90M_GATE_PH"
)
MAG = 200_000
# _________________
# se conformer à l'utilisation de dataclass ? variables du main dépendant de Block et d'autres non
# layers
# topcell
# precision

# excel_file = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy-proto_data.xlsx"
# test_calibre_rulers = "/work/opc/all/users/banger/dev/semchef/examples/calibre_rulers.xml"

# TODO
# overlap input data with GUI selection
# get_eps_data() + write_in_file() to call in hss_creator ?
# output json format recipe if modification needs to be done afterwards -> in hss creator output json from df or from str ?
# toggle -> send on sem ? yes or no
# export recipe to a formatted name -> ex: user_techno_maskset_layers_more


def run_recipe_creation_w_measure(upload=False):
    '''this is the real main function which runs the flow with the measure - "prod" function'''    
    get_user_path_instance = GetUserInputs()
    parser = get_user_path_instance.get_user_secured_path("Enter a path to your coordinate source :\n")
    layout = get_user_path_instance.get_user_secured_path("Enter a path to your layout :\n")
    layers = get_user_path_instance.get_user_secured_list_int_float("Enter layer(s) number list (separated by comma + space ', ' each time):\n")
    block = Block(layout)
    print('\n______________________RUNNING RECIPE CREATION______________________\n')
    # TODO change selection logic
    try:
        parser_instance = CalibreXMLParser(parser, block.precision)
        data_parsed = parser_instance.parse_data()
    except ParseError:
        parser_instance = SsfileParser(parser, is_genepy=True)
        data_parsed = parser_instance.parse_data().iloc[60:70]
    # TODO pass FileParser instance directly (and optional slice?)
    measure_instance = Measure(data_parsed, block.layout_path, layers, unit=parser_instance.unit, precision=block.precision)  # TODO remove unit -> should be managed in parsers ???
    output_measure = measure_instance.run_measure()
    # TODO core data ?
    output_measure['magnification'] = MAG
    EPS_DataFrame = DataFrameToEPSData(output_measure)
    # with open('/work/opc/all/users/chanelir/semrc/tests/output_measure.test', 'w') as f:
    #     f.write(output_measure.to_csv(index=False))
    # EPS_Data = EPS_DataFrame.get_eps_data("X90M_GATE_PH")
    EPS_Data = EPS_DataFrame.get_eps_data(TESTCASE_GENEPY["mp_template"])
    runHssCreation = HssCreator(eps_dataframe=EPS_Data, layers=int(float(layers[0].split(',')[0])), layout=block.layout_path, topcell=block.topcell, precision=block.precision)
    runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(runHssCreation.path_output_file)
        rcpd.upload_gds(block.layout)


if __name__ == "__main__":
    run_recipe_creation_w_measure()
