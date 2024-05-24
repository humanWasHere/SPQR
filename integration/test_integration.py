import time
from pathlib import Path
from typing import Type

from app.data_structure import Block
from app.export_hitachi.eps_data import DataFrameToEPSData
from app.export_hitachi.hss_creator import HssCreator
from app.interfaces import recipedirector as rcpd
from app.measure.measure import Measure
from app.parsers import FileParser, CalibreXMLParser, SSFileParser

# TODO: internalize test sfiles
TESTFILES = Path(__file__).resolve().parents[1] / "tests" / "testfiles"


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
        coord_file=TESTFILES / "ssfile_proto.txt",
        layout=TESTFILES / "COMPLETED_TEMPLATE.gds",
        layers=["1.0"],
        rows=(60, 70),
        mag=200_000,
        mp_template="Width_Default",
        # step="PH"
    )
    assert True  # TODO


def test_rulers():
    run_recipe(
        parser=CalibreXMLParser,
        coord_file="/work/opc/all/users/banger/X90M/GATE/rulers_product.xml",
        layout="/work/opc/all/users/banger/X90M/GATE/466_Product_clips.oas",
        layers=["13.0"],
        rows=None,
        mag=200_000,
        mp_template="X90M_GATE_PH",
        # step="PH"
    )
    assert True
