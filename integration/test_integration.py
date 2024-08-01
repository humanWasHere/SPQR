import time
from pathlib import Path
from typing import Type

from app.data_structure import Block
from app.export_hitachi.eps_data import EPSData
from app.export_hitachi.hss_creator import HssCreator
from app.interfaces import recipedirector as rcpd
from app.measure.measure import Measure
from app.parsers import FileParser, CalibreXMLParser, SSFileParser, OPCFieldReverse, HSSParser, JSONParser

# TODO: internalize test sfiles
TESTFILES = Path(__file__).resolve().parents[1] / "tests" / "testfiles"


# FIXME since we use the same format as app_config.json
# -> should we get the conf from the file in assets ?
def json_conf_maker(recipe_name: str, output_dir: str | Path, file_parser: str| Path,
                    layout: str | Path, layers: list[str], ap1_template: str, ap1_mag: int,
                    ep_template: str, eps_template: str, magnification: int, mp_template: str,
                    step: str, origin_x_y: list[float], step_x_y: list[float],
                    n_rows_cols: list[int], ap1_offset: list[float]):
    json_conf = {
        "recipe_name": recipe_name,
        "output_dir": output_dir,
        "parser": file_parser,
        "layout": layout,
        "layers": layers,
        "ap1_template": ap1_template,
        "ap1_mag": ap1_mag,
        "ep_template": ep_template,
        "eps_template": eps_template,
        "magnification": magnification,
        "mp_template": mp_template,
        "step": step,
        "origin_x_y": origin_x_y,
        "step_x_y": step_x_y,
        "n_rows_cols": n_rows_cols,
        "ap1_offset": ap1_offset
    }
    return json_conf


def run_recipe(json_conf, parser: Type[FileParser], upload=False, rows=None) -> None:

    # TODO condition opcfield
    parser_instance = parser(json_conf['parser'])
    block = Block(json_conf['layout'])
    start = time.time()
    measure_instance = Measure(parser_instance, block, json_conf['layers'], offset=None, row_range=rows)
    output_measure = measure_instance.run_measure(output_dir=json_conf['output_dir'], recipe_name=json_conf['recipe_name'])
    end = time.time()
    # output_measure['magnification'] = mag

    # EPS_DataFrame = EPSData(output_measure)
    # EPS_Data = EPS_DataFrame.get_eps_data(mp_template)

    # FIXME should we keep EPS_Data out of HSSCreator ?

    # mask_layer = int(layers[0].split('.')[0])
    runHssCreation = HssCreator(core_data=output_measure, block=block, json_conf=json_conf)
    runHssCreation.write_in_file()

    print(f"Measure time: {end-start:.6f} s")

    if upload:
        rcpd.upload_csv(runHssCreation.output_path)
        rcpd.upload_gds(json_conf['layout'])


def test_genepy():
    json_conf = json_conf_maker(
        recipe_name = "test_integration_genepy",
        output_dir = TESTFILES / "recipe_output",
        file_parser = TESTFILES / "ssfile_proto.txt",
        layout = TESTFILES / "COMPLETED_TEMPLATE.gds",
        layers = ["1.0"],
        ap1_template = "",
        ap1_mag = "",
        ep_template = "",
        eps_template = "",
        magnification = 200_000,
        mp_template = "Width_Default",
        step = "PH",
        origin_x_y = [],
        step_x_y = [],
        n_rows_cols = [],
        ap1_offset = []
    )
    run_recipe(
        json_conf=json_conf,
        parser=SSFileParser,
        rows=[[60, 70]]
    )
    assert True  # TODO


def test_rulers():
    json_conf = json_conf_maker(
        recipe_name = "test_integration_rulers",
        output_dir = TESTFILES / "recipe_output",
        file_parser = "/work/opc/all/users/banger/X90M/GATE/rulers_product.xml",
        layout = "/work/opc/all/users/banger/X90M/GATE/466_Product_clips.oas",
        layers = ["13.0"],
        ap1_template = "",
        ap1_mag = "",
        ep_template = "",
        eps_template = "",
        magnification = 200_000,
        mp_template = "X90M_GATE_PH",
        step = "PH",
        origin_x_y = [],
        step_x_y = [],
        n_rows_cols = [],
        ap1_offset = []
    )
    run_recipe(
        json_conf=json_conf,
        parser=CalibreXMLParser,
        rows=None,
    )
    assert True

def test_opcfield():
    json_conf = json_conf_maker(
        recipe_name = "test_integration_opcfield",
        output_dir = TESTFILES / "recipe_output",
        file_parser = "",
        layout = "/prj/opc/all/users/bigarnen/P18/GDS/1808A_OPCMACRO_OPCF_FGAT.oas",
        layers = ["7.0"],
        ap1_template = "",
        ap1_mag = "",
        ep_template = "",
        eps_template = "",
        magnification = 200_000,
        mp_template = "Width_Default",
        step = "PH",
        origin_x_y = [12888.5, 16507.5],
        step_x_y = [10, 10],
        n_rows_cols = [93, 33],
        ap1_offset = [2.75, 0]
    )
    run_recipe(
        json_conf=json_conf,
        # give instance
        parser=OPCFieldReverse,
        rows=None,
    )
    assert True

def test_csv():
    json_conf = json_conf_maker(
        recipe_name = "test_integration_csv",
        output_dir = TESTFILES / "recipe_output",
        file_parser = "/work/opc/all/users/chanelir/spqr-assets/json_csv_recipes/test_env_genepy.csv",
        layout = "/work/opc/all/users/chanelir/spqr-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
        layers = ["1.0"],
        ap1_template = "",
        ap1_mag = "",
        ep_template = "",
        eps_template = "",
        magnification = 200_000,
        mp_template = "X90M_GATE_PH",
        step = "PH",
        origin_x_y = [],
        step_x_y = [],
        n_rows_cols = [],
        ap1_offset = []
    )
    run_recipe(
        json_conf=json_conf,
        parser=HSSParser,
        rows=[[60, 70]]
    )
    assert True

def test_json():
    json_conf = json_conf_maker(
        recipe_name = "test_integration_json",
        output_dir = TESTFILES / "recipe_output",
        file_parser = "/work/opc/all/users/chanelir/spqr-assets/json_csv_recipes/test_env_genepy.json",
        layout = "/work/opc/all/users/chanelir/spqr-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
        layers = ["1.0"],
        ap1_template = "",
        ap1_mag = "",
        ep_template = "",
        eps_template = "",
        magnification = 200_000,
        mp_template = "X90M_GATE_PH",
        step = "PH",
        origin_x_y = [],
        step_x_y = [],
        n_rows_cols = [],
        ap1_offset = []
    )
    run_recipe(
        json_conf=json_conf,
        parser=JSONParser,
        rows=[[60, 70]]
    )
    assert True
