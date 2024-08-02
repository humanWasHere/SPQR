import json
import time
from pathlib import Path
from typing import Type

import pytest

from app.data_structure import Block
# from app.export_hitachi.eps_data import EPSData
from app.export_hitachi.hss_creator import HssCreator
from app.interfaces import recipedirector as rcpd
from app.measure.measure import Measure
from app.parsers import FileParser, CalibreXMLParser, SSFileParser, OPCFieldReverse, HSSParser, JSONParser

# TODO: internalize test sfiles
APP_CONFIG = Path(__file__).resolve().parents[2] / "assets" / "app_config.json"
app_config_content = json.loads(APP_CONFIG.read_text())


def run_recipe(json_conf, parser: Type[FileParser], upload=False, rows=None) -> None:

    # TODO condition opcfield
    if parser == OPCFieldReverse:
        origin_x, origin_y = json_conf['origin_x_y']
        step_x, step_y = json_conf['step_x_y']
        n_rows, n_cols = json_conf['n_cols_rows']
        ap_x, ap_y = json_conf['ap1_offset']
        parser_instance = OPCFieldReverse(origin_x=origin_x, origin_y=origin_y, step_x=step_x, step_y=step_y,
                                          n_rows=n_rows, n_cols=n_cols, ap_x=ap_x, ap_y=ap_y)
    else:
        parser_instance = parser(json_conf['coord_file'])

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


def test_genepy(tmp_path):
    json_conf = app_config_content.get('genepy')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=SSFileParser,
        rows=[[60, 70]]
    )
    assert True  # TODO


def test_rulers(tmp_path):
    json_conf = app_config_content.get('calibre_rulers')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=CalibreXMLParser,
        rows=None,
    )
    assert True


def test_opcfield(tmp_path):
    json_conf = app_config_content.get('opcfield')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        # give instance
        parser=OPCFieldReverse,
        rows=[[1, 10]],
    )
    assert True


# @pytest.mark.skip(reason="runtime")
def test_csv(tmp_path):
    json_conf = app_config_content.get('csv')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=HSSParser,
        rows=[[60, 70]]
    )
    assert True


@pytest.mark.skip(reason="runtime")
def test_json(tmp_path):
    # json_conf = json_conf_maker(
    #     recipe_name = "test_integration_json",
    #     output_dir = TESTFILES / "recipe_output",
    #     file_parser = "/work/opc/all/users/chanelir/spqr-assets/json_csv_recipes/test_env_genepy.json",
    #     layout = "/work/opc/all/users/chanelir/spqr-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
    #     layers = ["1.0"],
    #     ap1_template = "",
    #     ap1_mag = "",
    #     ep_template = "",
    #     eps_template = "",
    #     magnification = 200_000,
    #     mp_template = "X90M_GATE_PH",
    #     step = "PH",
    #     origin_x_y = [],
    #     step_x_y = [],
    #     n_cols_rows = [],
    #     ap1_offset = []
    # )
    json_conf = app_config_content.get('json')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=JSONParser,
        rows=[[60, 70]]
    )
    assert True
