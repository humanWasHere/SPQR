import json
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

from app.data_structure import Block
from app.export_hitachi.hss_creator import HssCreator
from app.parsers.json_parser import JSONParser


# TODO make relative file path for "test_template.json"

# LAYOUT_TESTCASE = Path(__file__).resolve().parents[1] / "testfiles" / "COMPLETED_TEMPLATE.gds"
TEST_TEMPLATE = Path(__file__).resolve().parents[2] / "testfiles" / "test_template.json"


class TestHssCreator:

    # TODO variabiliser les chemins de fichier
    test_json_user_config = {
        "recipe_name": "test_temp_output",
        "output_dir": Path(__file__).resolve().parent,
        "coord_file": "/work/opc/all/users/chanelir/spqr-assets/spqr_test_ressources/ssfile_proto.txt",
        "layout": "/work/opc/all/users/chanelir/spqr-assets/spqr_test_ressources/COMPLETED_TEMPLATE.gds",
        "layers": ["1.0"],
        "ap1_template": "",
        "ap1_mag": 50000,
        "ep_template": "",
        "eps_template": "OPC_EPS_Template",
        "magnification": 200000,
        "mp_template": "X90M_GATE_PH",
        "step": "PH",
        "opcfield_x": "",
        "opcfield_y": "",
        "step_x": "",
        "step_y": "",
        "num_step_x": "",
        "num_step_y": ""
    }

    @pytest.fixture
    def block_instance(self):
        """Mock the execution of layout peek"""
        mock_block = mock.create_autospec(Block, instance=True)
        mock_block.layout_path = "fake.oas"
        mock_block.topcell = "TOP"
        mock_block.precision = 1000
        return mock_block

    @pytest.fixture
    def core_data(self):
        return pd.DataFrame({
            'name': ['Name1', 'Name2', 'Name3'],
            'x': [5500, 5500, 5500],
            'y': [-94500, -94500, -94500],
            'x_ap': [0, 0, 0],
            'y_ap': [0, 0, 0],
            'x_dim': [0, 0, 0],
            'y_dim': [0, 0, 0]
        })

    @pytest.fixture
    def hss_instance(self, block_instance, core_data):
        return HssCreator(core_data=core_data, block=block_instance, json_conf=self.test_json_user_config)

    # @pytest.fixture
    # def test_file_hss_creator(tmp_path, filename, content):
    #     tmp_file = tmp_path / filename
    #     tmp_file.write_text(content)
    #     return tmp_file

    def test_fill_with_eps_data(self, hss_instance):
        '''tests that dataframe_to_eps_data.py to check if it returns a dataframes'''
        # TODO test très impertinent -> il check l'init de la fonction
        # Act
        hss_instance.fill_with_eps_data()

        # Assert
        # We test that it still returns a dataframe
        # EPS_Data is already test covered in its own
        assert isinstance(hss_instance.table_sections["<EPS_Data>"], pd.DataFrame)

    def test_get_set_section(self, hss_instance):
        """Tests the calls to SectionMaker. SectionMaker is tested separately"""
        # Arrange

        # Act
        hss_instance.get_set_section()

        # Assert
        # We test that it still returns a dataframe
        for section in hss_instance.table_sections.values():
            assert isinstance(section, pd.DataFrame)

    def test_dataframe_to_hss(self, hss_instance):
        '''tests that the function of hss creation works'''

        # FIXME too fat
        # TODO assert line per line?
        expected_hss: str = (
            "<FileID>\nLIDP00\n<Version>\n6\n<Revision>\n0\n"
            "<CoordinateSystem>\n#Type,ACD_Type\n1,1\n"
            "<GPCoordinateSystem>\n#Type\n1\n"
            "<Unit>\n#Coordinate,MP_Box\n1,1\n"
            "<GP_Data>\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_Mag,GP_Rot\n1,1,0,0,chef_OM_default,210,\n2,1,0,0,chef_SEM_default,12000,0.0\n"  # beware \ at [0.0, 0.0] or a str w/ ""
            '<EPS_Data>\n#EPS_ID,Type1,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type2,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type3,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type4,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type5,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type6,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type7,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_X,EP_Mag_Y,EP_Rot,Type8,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type9,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type10,EP_ABCC_X,EP_ABCC_Y,Type11,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_SA_Out,MP1_MeaLeng,MP1_Direction,Type12,MP2_X,MP2_Y,MP2_Template,MP2_PNo,MP2_DNo1,MP2_DNo2,MP2_Name,MP2_TargetCD,MP2_PosOffset,MP2_SA_In,MP2_SA_Out,MP2_MeaLeng,MP2_Direction,Type13,MP3_X,MP3_Y,MP3_Template,MP3_PNo,MP3_DNo1,MP3_DNo2,MP3_Name,MP3_TargetCD,MP3_PosOffset,MP3_SA_In,MP3_SA_Out,MP3_MeaLeng,MP3_Direction,Type14,MP4_X,MP4_Y,MP4_Template,MP4_PNo,MP4_DNo1,MP4_DNo2,MP4_Name,MP4_TargetCD,MP4_PosOffset,MP4_SA_In,MP4_SA_Out,MP4_MeaLeng,MP4_Direction\n1,1,-300000000,-300000000,1,chaine,1,chaine,chaine,chaine,chaine,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,1000,1000,"[0.0, 0.0]",2,-10000,-10000,0,2,-10000,-10000,0,2,-10000,-10000,2,-300000000,-300000000,chaine,1,0,0,chaine,-200000,-200000,0,0,1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n'
            "<GPA_List>\n#GPA_No,Chip_X,Chip_Y,GP_ID\n1,2,4,1\n2,8,4,1\n3,8,4,2\n4,2,4,2\n5,5,6,2\n6,5,2,2\n"
            "<GP_Offset>\n#Offset_X,Offset_Y\n0,0\n"
            "<EPA_List>\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode\n1,6,4,1,1\n"
            "<IDD_Cond>\n#DesignData,CellName,DCRot,DCOffsetX,DCOffsetY,Tone\n,,0,0,0,0\n"
            "<IDD_Layer_Data>\n#LayerNo,DataType,Type,Level,DUMMY,Tone,ColorNo,FillNo,LayerName\n0,114,0,,,0,4,8,TARGET\n13,4,0,,,0,4,2,DUMMIES\n13,31,0,,,0,4,8,NOOPC\n13,100,2,,,0,13,1,SRAF\n13,0,2,,,0,4,1,OPC\n"
            "<ImageEnv>\n#Type,Size,CompressSW,Quality,MeasCur,CrossCur,AreaCur,DDS,MeasVal,LinePro,umMark\n0,0,0,32,0,1,0,0,0,0,0\n1,0,0,32,0,0,0,0,0,0,0\n2,0,0,32,0,0,0,0,0,0,0"
        )

        # Act
        # FIXME dependency
        json_template_instance = JSONParser(TEST_TEMPLATE).json_to_section_dicts()
        hss_instance.constant_sections = json_template_instance.constant_sections
        hss_instance.table_sections = json_template_instance.table_sections
        hss_str = hss_instance.dataframe_to_hss()

        # Assert
        assert isinstance(hss_str, str)
        assert hss_str == expected_hss

    def test_rename_eps_data_header(self, hss_instance):
        '''checks that the method renames "TypeN" column name in "Type"'''
        # Arrange
        # passes with \n
        string_to_edit = "Type1,Type12,Type100\n1,2,3\n1,2,3\n"
        expected_new_string = "Type,Type,Type\n1,2,3\n1,2,3\n"

        # Act
        new_string = hss_instance.rename_eps_data_header(string_to_edit)

        # Assert
        assert new_string == expected_new_string

    def test_set_commas_afterwards(self, hss_instance):
        '''checks that the method adds the correct number of commas at the end of each line'''
        # TODO check if it corresponds to correct commas number
        # Arrange
        string_to_modify_1 = (
            "<GP_Data>\n"
            "GP_ID,Type,GP_X,GP_Y,GP_Template,GP_Mag,GP_Rot\n"
            "1,1,20,20,chef_OM_default,210,90\n")
        expected_modified_string_1 = (
            "<GP_Data>,,,,,,\n"
            "GP_ID,Type,GP_X,GP_Y,GP_Template,GP_Mag,GP_Rot\n"
            "1,1,20,20,chef_OM_default,210,90\n")

        # Act
        modified_string_1 = hss_instance.set_commas_afterwards(string_to_modify_1)

        # Assert
        assert modified_string_1 == expected_modified_string_1

    def test_output_dataframe_to_json(self, hss_instance):
        # TODO change dataframe
        # Arrange
        # hss_creator = HssCreator(pd.DataFrame(), block=block_instance,)

        hss_instance.constant_sections = {'<FileID>': 'LIDP00', '<Version>': 6, '<Revision>': 0}
        hss_instance.table_sections = {
            '<CoordinateSystem>': pd.DataFrame([{'Type': 1, 'ACD_Type': 1}]),
            '<Unit>': pd.DataFrame([{'Coordinate': 1, 'MP_Box': 1}])
        }

        expected_json_content = {
            '<FileID>': 'LIDP00',
            '<Version>': 6,
            '<Revision>': 0,
            '<CoordinateSystem>': {
                'Type': [
                    1
                ],
                'ACD_Type': [
                    1
                ]
            },
            '<Unit>': {
                'Coordinate': [
                    1
                ],
                'MP_Box': [
                    1
                ]
            }
        }
        expected_json_str = json.dumps(expected_json_content, indent=4)

        # Act
        hss_instance.output_dataframe_to_json()
        with open(str(hss_instance.recipe_output_file), 'r') as json_file:
            content = json_file.read()

        # Assert
        assert hss_instance.recipe_output_file.exists()
        assert content == expected_json_str
        assert hss_instance.recipe_output_file.suffix == ".json"

    def test_output_dataframe_to_csv(self, hss_instance):
        # Arrange

        # Act
        hss_instance.output_dataframe_to_csv()

        # Assert
        assert hss_instance.recipe_output_file.exists()
        assert hss_instance.recipe_output_file.suffix == ".csv"

    def test_write_in_file(self, hss_instance):
        '''checks for file writing and content written'''

        # Arrange
        print(self.test_json_user_config['output_dir'])
        output_recipe_file_path = Path(self.test_json_user_config['output_dir'] / (self.test_json_user_config['recipe_name'] + ".csv"))
        output_json_file_path = Path(self.test_json_user_config['output_dir'] / (self.test_json_user_config['recipe_name'] + ".json"))

        # Act
        hss_instance.write_in_file()

        # Assert
        # asserts that there is some content in the test files
        assert output_recipe_file_path.exists(), "The file does not exist."
        assert output_json_file_path.exists(), "The file does not exist."
        with open(hss_instance.recipe_output_file.with_suffix(".csv"), 'r') as file:
            content = file.read()
            assert content, "The file is empty."
        with open(hss_instance.recipe_output_file.with_suffix(".json"), 'r') as file:
            content = file.read()
            assert content, "The file is empty."
        output_recipe_file_path.unlink()
        output_json_file_path.unlink()
