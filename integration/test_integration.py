import time
from typing import Type

from app.data_structure import Block
from app.export_hitachi.eps_data import DataFrameToEPSData
from app.export_hitachi.hss_creator import HssCreator
from app.interfaces import recipedirector as rcpd
from app.measure.measure import Measure
from app.parsers import FileParser, CalibreXMLParser, SSFileParser


def run_recipe(coord_file: str, parser: Type[FileParser], layout: str, layers: list[str],
               mp_template='', mag=200_000, upload=False, rows=None) -> None:

    parser_instance = parser(coord_file)
    block = Block(layout)
    start = time.time()
    measure_instance = Measure(parser_instance, block, layers, row_range=rows)
    output_measure = measure_instance.run_measure()
    end = time.time()
    output_measure['magnification'] = mag

    EPS_DataFrame = DataFrameToEPSData(output_measure)
    EPS_Data = EPS_DataFrame.get_eps_data(mp_template)

    mask_layer = int(layers[0].split('.')[0])
    runHssCreation = HssCreator(
        eps_dataframe=EPS_Data, layers=mask_layer, block=block, recipe_name="test")
    runHssCreation.write_in_file()

    print(f"Measure time: {end-start:.6f} s")

    if upload:
        rcpd.upload_csv(runHssCreation.output_path)
        rcpd.upload_gds(layout)


def test_genepy():
    run_recipe(
        parser=SSFileParser,
        coord_file="/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt",
        layout="/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
        layers=["1.0"],
        rows=(60, 70),
        mag=200_000,
        mp_template="X90M_GATE_PH",
        # step="PH"
    )
    assert True  # TODO
