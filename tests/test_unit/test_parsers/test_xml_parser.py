# from io import StringIO
import numpy as np
import pandas as pd
import pytest

import lxml.etree as ET

from app.parsers.xml_parser import CalibreXMLParser


XML_RULER_CONTENT = """<?xml version="1.0" standalone="yes"?>
<rulers>
  <version>1.0</version>
  <ruler>
    <type>botharrows</type>
    <units>micrometer</units>
    <tickmarks>auto</tickmarks>
    <height>8</height>
    <comment>EPS1</comment>
    <format>%.3f</format>
    <points>
      <point>
        <x>-625186.000000</x>
        <y>1030530.000000</y>
      </point>
      <point>
        <x>-622574.000000</x>
        <y>1025150.000000</y>
      </point>
    </points>
  </ruler>
</rulers>"""


XML_CLIP_CONTENT = """<?xml version="1.0" standalone="yes"?>
<!-- Clips are managed by the application. -->
<clips>
  <version>1.0</version>
  <units>micron</units>
  <clip>
    <name>Clip 10</name>
    <x>86.670</x>
    <y>268.999</y>
    <width>21.016</width>
    <height>19.670</height>
    <cellname>T466A1_TOP_DUMMIES_MK_MB</cellname>
  </clip>
</clips>
"""


@pytest.fixture()
def ruler_xml_file(tmp_path):
    tmp_file = tmp_path / "tmp_ruler.xml"
    tmp_file.write_text(XML_RULER_CONTENT)
    return tmp_file


@pytest.fixture()
def clip_xml_file(tmp_path):
    tmp_file = tmp_path / "tmp_clip.clips"
    tmp_file.write_text(XML_CLIP_CONTENT)
    return tmp_file


def test_init_ruler_from_path(ruler_xml_file):
    parser = CalibreXMLParser(ruler_xml_file)
    assert parser.tree is not None
    assert parser.type == "rulers"
    assert parser.unit == "dbu"


def test_init_clip_from_path(clip_xml_file):
    parser = CalibreXMLParser(clip_xml_file)
    assert parser.tree is not None
    assert parser.type == "clips"
    assert parser.unit == "micron"


# def test_parse_from_string():
#     parser = CalibreXMLParser(StringIO(RULER_XML_CONTENT))
#     assert parser.tree is not None

def test_parse_from_element_tree():
    tree = ET.fromstring(XML_RULER_CONTENT).getroottree()  # lxml
    parser = CalibreXMLParser(tree)
    assert parser.tree is not None


def test_gen_rows_ruler(ruler_xml_file):
    parser = CalibreXMLParser(ruler_xml_file)
    expected_rows = ("EPS1", -623880, 1027840)
    rows = next(parser.gen_rows_ruler())
    assert rows == expected_rows


def test_gen_rows_clip(clip_xml_file):
    parser = CalibreXMLParser(clip_xml_file)
    expected_rows = ("Clip 10", 97.178, 278.834)
    rows = next(parser.gen_rows_clip())
    assert rows == expected_rows


@pytest.mark.parametrize("xml_content", ["<other></other>", ""])
def test_incorrect_xml_type(xml_content):
    # incorrect_xml_content = "<clips></clips>"
    incorrect_xml_content = xml_content
    with pytest.raises((ET.ParseError, ValueError)):
        tree = ET.fromstring(incorrect_xml_content).getroottree()
        parser = CalibreXMLParser(tree)
        parser.parse_data()


@pytest.mark.parametrize("xml_file", ["ruler_xml_file", "clip_xml_file"])
def test_parse_data(xml_file, request):
    xml_file = request.getfixturevalue(xml_file)
    parser = CalibreXMLParser(xml_file)
    df = parser.parse_data()
    # FIXME make post_parse?
    assert not df.empty
    assert set(df.columns).issuperset({'name', 'x', 'y', 'x_ap', 'y_ap'})
    # TODO pd.testing.assert_frame_equal


def test_parse_data_dbu(clip_xml_file):
    expected = pd.DataFrame(dict(name=["Clip_10"], x=[971780], y=[2788340], x_ap=np.nan, y_ap=np.nan))
    parser = CalibreXMLParser(clip_xml_file)
    actual = parser.parse_data_dbu(10000)
    pd.testing.assert_frame_equal(actual, expected)


# def test_validate(ruler_xml_file):
#     parser = CalibreXMLParser(ruler_xml_file)
    # parser.parse_data_decorated()
