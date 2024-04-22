import pytest
import pandas as pd
from app.parsers.ssfile_parser import SSFileParser


GENEPY_FILE_CONTENT = \
    """UNIT_COORD	X_coord_Pat	Y_coord_Pat	X_coord_Addr	Y_coord_Addr	Location	Name
DBU	55000	-945000	55000	-910000	A7	CDvP_CD50_P310_V
DBU	110000	-945000	110000	-910000	B7	CDvP_CD70_P310_V
"""


@pytest.fixture()
def genepy_file(tmp_path):
    tmp_file = tmp_path / "tmp_genepy.csv"
    tmp_file.write_text(GENEPY_FILE_CONTENT)
    return tmp_file


def test_coord_to_relative():
    relative_coords = pd.DataFrame(dict(x=[55000], y=[-945000], x_ap=[0], y_ap=[35000]))

    absolute_coords = pd.DataFrame(dict(x=[55000], y=[-945000], x_ap=[55000], y_ap=[-910000]))
    actual_data = SSFileParser.change_coord_to_relative(absolute_coords)

    pd.testing.assert_frame_equal(actual_data, relative_coords)


def test_genepy_to_dataframe(genepy_file):
    expected_data = pd.DataFrame(dict(
        UNIT_COORD=["DBU", "DBU"],
        X_coord_Pat=[55000, 110000],
        Y_coord_Pat=[-945000, -945000],
        X_coord_Addr=[55000, 110000],
        Y_coord_Addr=[-910000, -910000],
        Location=["A7", "B7"],
        Name=["CDvP_CD50_P310_V", "CDvP_CD70_P310_V"]
    ))
    
    parser = SSFileParser(genepy_file, is_genepy=True)
    actual_data = parser.genepy_to_dataframe()

    pd.testing.assert_frame_equal(actual_data, expected_data)
    assert parser.unit == "dbu"


def test_post_parse(genepy_file):
    expected_data = pd.DataFrame(dict(
        UNIT_COORD=["DBU", "DBU"],
        x=[55000, 110000],
        y=[-945000, -945000],
        x_ap=[0, 0],
        y_ap=[35000, 35000],
        Location=["A7", "B7"],
        name=["CDvP_CD50_P310_V", "CDvP_CD70_P310_V"]
    ))
    
    parser = SSFileParser(genepy_file, is_genepy=True)
    parser.data = pd.DataFrame(dict(
        UNIT_COORD=["DBU", "DBU"],
        X_coord_Pat=[55000, 110000],
        Y_coord_Pat=[-945000, -945000],
        X_coord_Addr=[55000, 110000],
        Y_coord_Addr=[-910000, -910000],
        Location=["A7", "B7"],
        Name=["CDvP_CD50_P310_V", "CDvP_CD70_P310_V"]
    ))
    parser.post_parse()

    pd.testing.assert_frame_equal(parser.data, expected_data)


def test_parse_data(genepy_file):
    expected_data = pd.DataFrame(dict(
        UNIT_COORD=["DBU", "DBU"],
        x=[55000, 110000],
        y=[-945000, -945000],
        x_ap=[0, 0],
        y_ap=[35000, 35000],
        Location=["A7", "B7"],
        name=["CDvP_CD50_P310_V", "CDvP_CD70_P310_V"]
    ))
    
    parser = SSFileParser(genepy_file, is_genepy=True)
    parser.parse_data()

    pd.testing.assert_frame_equal(parser.data, expected_data)


# def test_ssfile_to_dataframe(self):
#     pass
