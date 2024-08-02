from pathlib import Path

import pytest
from pydantic import ValidationError

from app.interfaces.input_checker import BaseRecipe, CoordFile, OPCField


TESTFILES = Path(__file__).resolve().parents[2] / "testfiles"


@pytest.fixture
def valid_recipe_data():
    return {
        'recipe_name': "test_recipe",
        'output_dir': "./",
        'coord_file': str(TESTFILES / "ssfile_proto.txt"),
        'layout': str(TESTFILES / "COMPLETED_TEMPLATE.gds"),
        'layers': ["1.0"],
        'ap1_template': 'AP1_45K',
        'ap1_mag': 45000,
        'ap1_offset': [0.35, -4.4],
        'ep_template': "EP_16F",
        'eps_template': "EPS_Default",
        'magnification': 200000,
        'polarity': 'dark',
        'mp_template': "Width_Default",
        'step': "PH",
        'origin_x_y': [0.5, 0.5],
        'step_x_y': [4.5, 4.5],
        'n_cols_rows': [9, 9]
    }


@pytest.fixture
def make_recipe_data(valid_recipe_data):
    """Parametrize the configuration using `factory as fixture' pattern"""
    def _make_recipe_data(**kwargs):
        recipe = valid_recipe_data.copy()
        recipe.update(kwargs)
        return recipe
    return _make_recipe_data


def test_recipe_with_all_fields(valid_recipe_data):
    CoordFile(**valid_recipe_data)
    OPCField(**valid_recipe_data)
    assert True


def test_recipe_with_minimum_fields():
    coordfile_recipe = {
        'coord_file': str(TESTFILES / "ssfile_proto.txt"),
        'layout': str(TESTFILES / "COMPLETED_TEMPLATE.gds"),
        'layers': ["13.100"],
        'step': "PH",
        'magnification': "200000",
    }
    coordfile = CoordFile(**coordfile_recipe)
    assert coordfile.coord_file == TESTFILES / "ssfile_proto.txt"
    assert coordfile.recipe_name is None
    assert coordfile.output_dir == Path.cwd()
    assert coordfile.layout == TESTFILES / "COMPLETED_TEMPLATE.gds"
    assert coordfile.layers == ["13.100"]
    assert coordfile.step == "PH"
    assert coordfile.magnification == 200_000
    assert coordfile.polarity == 'clear'
    assert coordfile.ap1_mag is None
    assert coordfile.ap1_offset is None
    assert coordfile.ap1_template == ''
    assert coordfile.ep_template == ''
    assert coordfile.eps_template == ''
    assert coordfile.mp_template == ''


@pytest.mark.parametrize("model, field, value", [
    # (BaseRecipe, 'layers', '13.100'),
    (BaseRecipe, 'output_dir', Path('.')),
    (BaseRecipe, 'step', ['PH', 'ET_HR']),
    pytest.param(BaseRecipe, 'polarity', 'DARK', marks=pytest.mark.xfail),
    pytest.param(BaseRecipe, 'offset', dict(x=1000, y=1000), marks=pytest.mark.xfail),
    (BaseRecipe, 'ap1_mag', 70000),
    (BaseRecipe, 'ap1_mag', '70000'),
    (BaseRecipe, 'ap1_offset', [1, 1]),
    (BaseRecipe, 'mp_template', 'MP_width'),
    (BaseRecipe, 'mp_template', {'line': 'MP_width'}),
    (OPCField, 'origin_x_y', [0.1, 0.1]),
    (OPCField, 'n_cols_rows', [9, 9]),
])
def test_validate_data(make_recipe_data, field, value, model):
    recipe_data = make_recipe_data(**{field: value})
    recipe = model(**recipe_data)
    # assert getattr(recipe, field) == value  # not possible with coercion
    assert recipe


@pytest.mark.parametrize("model, field, value", [
    (BaseRecipe, 'recipe_name', []),
    (BaseRecipe, 'output_dir', '/fake/path'),
    (BaseRecipe, 'layout', '/fake/path'),
    (BaseRecipe, 'layout', None),
    (BaseRecipe, 'layers', []),
    (BaseRecipe, 'step', []),
    (BaseRecipe, 'step', 'PHOTO'),
    (BaseRecipe, 'magnification', 'abc'),
    (BaseRecipe, 'polarity', 'DK'),
    (BaseRecipe, 'ap1_mag', 1000.5),
    (BaseRecipe, 'ap1_mag', -1000),
    (BaseRecipe, 'ap1_offset', [-1]),  # length
    (BaseRecipe, 'mp_template', ['MP_width']),  # str | dict
    (OPCField, 'origin_x_y', None),
    (OPCField, 'origin_x_y', 0.),  # list
    (OPCField, 'origin_x_y', [0.]),  # length
    (OPCField, 'n_cols_rows', [9.1, 9.1]),
    (CoordFile, 'coord_file', None),
    (CoordFile, 'coord_file', '/fake/path'),
    (CoordFile, 'coord_file', './'),
])
def test_fail_invalid_data(make_recipe_data, field, value, model):
    recipe_data = make_recipe_data(**{field: value})
    with pytest.raises((ValueError, ValidationError)):
        model(**recipe_data)


# @pytest.mark.parametrize("valid_data", [
#         dict(coord_file=None, origin_x_y='', step_x_y='', n_cols_rows=''),
#         dict(coord_file=None, mp_template=[]),
#     ], indirect=True)
# def test_invalid_data(valid_data):
    # with pytest.raises(ValueError):
    #     OPCField(**valid_data)
