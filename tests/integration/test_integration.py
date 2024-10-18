import json
import logging
import time
from pathlib import Path
from typing import Type

import pytest

from app.__main__ import model_to_parser
from app.data_structure import Block
# from app.export_hitachi.eps_data import EPSData
from app.export_hitachi.hss_creator import HssCreator
from app.interfaces.input_checker import validate_config_model
from app.measure.measure import Measure
from app.parsers import (FileParser, CalibreXMLParser, SSFileParser,
                         OPCFieldReverse, HSSParser, JSONParser)


# TODO: internalize test sfiles
@pytest.fixture
def app_config():
    config_path = Path(__file__).resolve().parents[2] / "assets" / "app_config.json"
    return json.loads(config_path.read_text())


def run_recipe(json_conf, parser: Type[FileParser], upload=False, rows=None) -> None:

    # TODO condition opcfield
    if parser == OPCFieldReverse:
        origin_x, origin_y = json_conf['origin_x_y']
        step_x, step_y = json_conf['step_x_y']
        n_cols, n_rows = json_conf['n_cols_rows']
        parser_instance = OPCFieldReverse(
            origin_x=origin_x, origin_y=origin_y,
            step_x=step_x, step_y=step_y,
            n_cols=n_cols, n_rows=n_rows)
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


def test_genepy(app_config, tmp_path):
    json_conf = app_config.get('genepy')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=SSFileParser,
        rows=[[60, 70]]
    )
    assert True  # TODO
    assert Path(json_conf['output_dir']).exists(), "Output directory does not exist"
    expected_output_files = [
        Path(json_conf['output_dir']) / f"{json_conf['recipe_name']}.csv",
        Path(json_conf['output_dir']) / f"{json_conf['recipe_name']}.json"
    ]
    for file in expected_output_files:
        assert file.exists(), f"Expected output file {file} does not exist"


def test_rulers(app_config, tmp_path):
    json_conf = app_config.get('calibre_rulers')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=CalibreXMLParser,
        rows=None,
    )
    assert True


def test_opcfield(app_config, tmp_path):
    json_conf = app_config.get('opcfield')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        # give instance
        parser=OPCFieldReverse,
        rows=[[1, 10]],
    )
    assert True


# def test_opcfield_measure_and_rename(app_config, tmp_path):
#     config = app_config.get('opcfield')
#     config.update(output_dir=tmp_path)
#     model = validate_config_model(config)
#     parser = model_to_parser(config)
#     block = Block(model.layout)
#     measure = Measure(parser, block, model.layers, row_range=[[1, 10]])
#     output_measure = measure.run_measure(model.output_dir, model.recipe_name)
#     # TODO test post-measure
#     assert True


# @pytest.mark.skip(reason="runtime")
def test_csv(app_config, tmp_path):
    json_conf = app_config.get('csv')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=HSSParser,
        rows=[[60, 70]]
    )
    assert True


@pytest.mark.skip(reason="runtime")
def test_json(app_config, tmp_path):
    json_conf = app_config.get('json')
    json_conf.update(output_dir=tmp_path)
    run_recipe(
        json_conf=json_conf,
        parser=JSONParser,
        rows=[[60, 70]]
    )
    assert True


def test_upload_recipe(test_files, capsys, caplog):
    """Test the upload command"""
    from app.interfaces import recipedirector
    caplog.set_level(logging.DEBUG)
    recipe_path = test_files / "test_env_genepy.csv"
    status = recipedirector.upload_csv(recipe_path, dry_run=True)
    print(status, capsys.readouterr(), caplog.text)
    assert status == 0
    assert 'sent' in caplog.text
    assert 'rsync error' not in caplog.text
