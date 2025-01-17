from pathlib import Path

import pandas as pd
import pytest

from app.parsers.json_parser import JSONParser, import_json


# TEST_TEMPLATE = Path(__file__).resolve().parents[2] / "testfiles" / "test_template.json"
TEST_TEMPLATE = Path(__file__).resolve().parents[3] / "assets" / "template_SEM_recipe.json"


class TestJsonParser:

    @pytest.fixture
    def json_parser_instance(self):
        return JSONParser(TEST_TEMPLATE)

    def test_import_json(self):
        '''checks that the template is correclty imported in memory'''
        # Arrange
        # TODO shorter version
        expected_output = {
            "<FileID>": "LIDP00",
            "<Version>": 6,
            "<Revision>": 0,
            "<CoordinateSystem>": {
                "Type": 1,
                "ACD_Type": 1
            },
            "<GPCoordinateSystem>": {
                "Type": 1
            },
            "<Unit>": {
                "Coordinate": 1,
                "MP_Box": 1
            },
            "<GP_Data>": {
                "GP_ID": [1, 2],
                "Type": [1, 1],
                "GP_X": [0, 0],
                "GP_Y": [0, 0],
                "GP_Template": ["chef_OM_default", "chef_SEM_default"],
                "GP_Mag": [210, 10000],
                "GP_Rot": [None, 0],
                "GP_Acceptance": [None, None]
            },
            "<EPS_Data>": {
                "EPS_ID": 1,
                "Type1": 1,
                "Move_X": 0,
                "Move_Y": 0,
                "Mode": 1,
                "EPS_Name": "chaine",
                "Ref_EPS_ID": 1,
                "EPS_Template": "chaine",
                "AP1_Template": "chaine",
                "AP2_Template": "chaine",
                "EP_Template": "chaine",
                "Type2": 2,
                "AP1_X": -300000000,
                "AP1_Y": -300000000,
                "AP1_Mag": 1000,
                "AP1_Rot": 0,
                "Type3": 2,
                "AP1_AF_X": -300000000,
                "AP1_AF_Y": -300000000,
                "AP1_AF_Mag": 0,
                "Type4": 2,
                "AP1_AST_X": -300000000,
                "AP1_AST_Y": -300000000,
                "AP1_AST_Mag": 0,
                "Type5": 2,
                "AP2_X": -300000000,
                "AP2_Y": -300000000,
                "AP2_Mag": 1000,
                "AP2_Rot": 0,
                "Type6": 2,
                "AP2_AF_X": -300000000,
                "AP2_AF_Y": -300000000,
                "AP2_AF_Mag": 0,
                "Type7": 2,
                "AP2_AST_X": -300000000,
                "AP2_AST_Y": -300000000,
                "AP2_AST_Mag": 0,
                "EP_Mag_X": 1000,
                "EP_Mag_Y": 1000,
                "EP_Rot": [0.0, 0.0],
                "Type8": 2,
                "EP_AF_X": -10000,
                "EP_AF_Y": -10000,
                "EP_AF_Mag": 0,
                "Type9": 2,
                "EP_AST_X": -10000,
                "EP_AST_Y": -10000,
                "EP_AST_Mag": 0,
                "Type10": 2,
                "EP_ABCC_X": -10000,
                "EP_ABCC_Y": -10000,
                "Type11": 2,
                "MP1_X": -300000000,
                "MP1_Y": -300000000,
                "MP1_Template": "chaine",
                "MP1_PNo": 1,
                "MP1_DNo1": 0,
                "MP1_DNo2": 0,
                "MP1_Name": "chaine",
                "MP1_TargetCD": -200000,
                "MP1_PosOffset": -200000,
                "MP1_SA_In": 0,
                "MP1_SA_Out": 0,
                "MP1_MeaLeng": 1,
                "MP1_Direction": 1,
                "Type12": "",
                "MP2_X": "",
                "MP2_Y": "",
                "MP2_Template": "",
                "MP2_PNo": "",
                "MP2_DNo1": "",
                "MP2_DNo2": "",
                "MP2_Name": "",
                "MP2_TargetCD": "",
                "MP2_PosOffset": "",
                "MP2_SA_In": "",
                "MP2_SA_Out": "",
                "MP2_MeaLeng": "",
                "MP2_Direction": "",
                "Type13": "",
                "MP3_X": "",
                "MP3_Y": "",
                "MP3_Template": "",
                "MP3_PNo": "",
                "MP3_DNo1": "",
                "MP3_DNo2": "",
                "MP3_Name": "",
                "MP3_TargetCD": "",
                "MP3_PosOffset": "",
                "MP3_SA_In": "",
                "MP3_SA_Out": "",
                "MP3_MeaLeng": "",
                "MP3_Direction": "",
                "Type14": "",
                "MP4_X": "",
                "MP4_Y": "",
                "MP4_Template": "",
                "MP4_PNo": "",
                "MP4_DNo1": "",
                "MP4_DNo2": "",
                "MP4_Name": "",
                "MP4_TargetCD": "",
                "MP4_PosOffset": "",
                "MP4_SA_In": "",
                "MP4_SA_Out": "",
                "MP4_MeaLeng": "",
                "MP4_Direction": ""
            },
            "<GPA_List>": {
                "GPA_No": [1, 2, 3, 4, 5],
                "Chip_X": [2, 8, 8, 2, 5],
                "Chip_Y": [4, 4, 4, 4, 2],
                "GP_ID": [1, 1, 2, 2, 2]
            },
            "<GP_Offset>": {
                "Offset_X": 0,
                "Offset_Y": 0
            },
            "<EPA_List>": {
                "EPA_No": None,
                "Chip_X": None,
                "Chip_Y": None,
                "EPS_ID": None,
                "Move_Mode": None
            },
            "<IDD_Cond>": {
                "DesignData": "",
                "CellName": "",
                "DCRot": 0,
                "DCOffsetX": 0,
                "DCOffsetY": 0,
                "Tone": 0
            },
            "<IDD_Layer_Data>": {
                "LayerNo": [0, 13, 13, 13, 13],
                "DataType": [114, 4, 31, 100, 0],
                "Type": [0, 0, 0, 2, 2],
                "Level": [None, None, None, None, None],
                "DUMMY": [None, None, None, None, None],
                "Tone": [0, 0, 0, 0, 0],
                "ColorNo": [4, 4, 4, 13, 4],
                "FillNo": [8, 2, 8, 1, 1],
                "LayerName": ["TARGET", "DUMMIES", "NOOPC", "SRAF", "OPC"]
            },
            "<ImageEnv>": {
                "Type": [0, 1, 2],
                "Size": [0, 0, 0],
                "CompressSW": [0, 0, 0],
                "Quality": [32, 32, 32],
                "MeasCur": [0, 0, 0],
                "CrossCur": [1, 0, 0],
                "AreaCur": [0, 0, 0],
                "DDS": [0, 0, 0],
                "MeasVal": [0, 0, 0],
                "LinePro": [0, 0, 0],
                "umMark": [0, 0, 0]
            },
            "<Recipe>": {
                "ClassName": "DG",
                "SEMCondNo": 2,
                "WaferProperty": 0,
                "SlotNum": 25,
                "SlotNo1SW": 0,
                "SlotNo2SW": 0,
                "SlotNo3SW": 0,
                "SlotNo4SW": 0,
                "SlotNo5SW": 0,
                "SlotNo6SW": 0,
                "SlotNo7SW": 0,
                "SlotNo8SW": 0,
                "SlotNo9SW": 0,
                "SlotNo10SW": 0,
                "SlotNo11SW": 0,
                "SlotNo12SW": 0,
                "SlotNo13SW": 0,
                "SlotNo14SW": 0,
                "SlotNo15SW": 0,
                "SlotNo16SW": 0,
                "SlotNo17SW": 0,
                "SlotNo18SW": 0,
                "SlotNo19SW": 0,
                "SlotNo20SW": 0,
                "SlotNo21SW": 0,
                "SlotNo22SW": 0,
                "SlotNo23SW": 0,
                "SlotNo24SW": 0,
                "SlotNo25SW": 0,
                "SlotNo26SW": 0,
                "AutoCalibrationSW": 0
            },
            "<MeasEnv_Exec>": {
                "WA_ExecMode": 0,
                "MA_ExecMode": 0,
                "ME_ExecMode": 0,
                "WA_ManualAssist": 1,
                "MA_ManualAssist": 0,
                "ME_ManualAssist": 0,
                "WA_ImageSave": 2,
                "MA_ImageSave": 2,
                "ME_ImageSave": 2
            },
            "<MeasEnv_MeasRes>": {
                "DiskSave": 1,
                "SendToHost": 1,
                "PrintOut": 0,
                "NetTransfer": 0,
                "Confirm": 0,
                "Method": 0,
                "LimitCheck": 0,
                "hiFrame": None
            }
        }

        # TODO parametrize different JSON inputs / check exceptions?
        # hss_creator = HssCreator(pd.DataFrame(), layers=1, block_instance, template=)

        # Act
        actual_json_output = import_json(TEST_TEMPLATE)
        # is_file_json = json.loads(actual_json_output)

        # Assert
        assert actual_json_output == expected_output
        # assert is_file_json == (dict, list)

    def test_parse_data(self, json_parser_instance):
        # Arrange
        expected_epsdata_section = pd.DataFrame({
            'name': ["chaine"],
            'x': [0],
            'y': [0],
            'x_ap': [-300000000],
            'y_ap': [-300000000]
        })

        # Act
        result = json_parser_instance.parse_data()

        # Assert
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected_epsdata_section)

    def test_json_to_section_dicts(self, json_parser_instance):
        '''tests that the template is correctly generated in several dataframes'''
        # Arrange
        expected_constants = {
            "<FileID>": "LIDP00",
            "<Version>": 6,
            "<Revision>": 0
        }
        expected_table = pd.DataFrame({"Type": [1], "ACD_Type": [1]})

        # Act
        result = json_parser_instance.json_to_section_dicts()

        print(result)
        print(expected_constants)
        print(expected_table)
        # Assert
        for section in json_parser_instance.table_sections.values():
            assert isinstance(section, pd.DataFrame)
        assert result.constant_sections == expected_constants
        pd.testing.assert_frame_equal(result.table_sections["<CoordinateSystem>"], expected_table)
