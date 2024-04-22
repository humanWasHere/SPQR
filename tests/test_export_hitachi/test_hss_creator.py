import pytest
from pathlib import Path
import pandas as pd
import json
import os
# import re
# from unittest.mock import MagicMock
from app.export_hitachi.hss_creator import HssCreator

# TODO make relative file path for "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"

# FIXME les colonnes nécessaire au fonctionnement du test seulement
# test les vrai fonctions et 1 chose à la fois -> sinon fonction est mal écrite

# faire des fixtures ???

# in creation of HssCreator() class, template argument should be empty the check if expected_data == template set in __init__ of the class

LAYOUT_TESTCASE = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"


class TestHssCreator:

    # @pytest.fixture
    # def test_file_hss_creator(tmp_path, filename, content):
    #     tmp_file = tmp_path / filename
    #     tmp_file.write_text(content)
    #     return tmp_file

    def test_import_json(self):
        '''checks that the template is correclty imported in memory'''
        # Arrange
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
                "GP_ID": 1,
                "Type": 1,
                "GP_X": 20,
                "GP_Y": 20,
                "GP_Template": "chef_OM_default",
                "GP_MAG": 210,
                "GP_ROT": 90
            },
            "<EPS_Data>": {
                "EPS_ID": 1,
                "Type1": 1,
                "Move_X": -300000000,
                "Move_Y": -300000000,
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
                "GPA_No": [1, 2, 3],
                "Chip_X": [2, 6, 3],
                "Chip_Y": [4, 4, 7],
                "GP_ID": [1, 1, 1]
            },
            "<GP_Offset>": {
                "Offset_X": 0,
                "Offset_Y": 0
            },
            "<EPA_List>": {
                "EPA_No": 1,
                "Chip_X": 6,
                "Chip_Y": 4,
                "EPS_ID": 1,
                "Move_Mode": 1
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
            }
        }

        # Act
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)
        actual_json_output = hss_creator.json_template
        # is_file_json = json.loads(actual_json_output)

        # Assert
        # TODO not sure about the error raised
        if actual_json_output != expected_output:
            print(actual_json_output)
            raise FileNotFoundError("File may not be in expected directory")
        assert actual_json_output == expected_output
        # assert is_file_json == (dict, list)

    def test_json_to_dataframe(self):
        '''tests that the template is correctly generated in several dataframes'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)

        # Act
        # FIXME dependency
        hss_creator.json_to_dataframe()

        # Assert
        # Assert first_level_df
        expected_first_level_df = {
            "<FileID>": "LIDP00",
            "<Version>": 6,
            "<Revision>": 0
        }
        assert hss_creator.constant_sections == expected_first_level_df

        # Assert <CoordinateSystem>
        expected_coordinate_system = pd.DataFrame(
            {"Type": [1], "ACD_Type": [1]})
        pd.testing.assert_frame_equal(hss_creator.table_sections["<CoordinateSystem>"], expected_coordinate_system)

        # Assert that all sections have been set as pd.DataFrame
        for key, value in hss_creator.table_sections.items():
            assert isinstance(value, (pd.DataFrame))

    def test_get_set_section(self):
        '''tests that sectionMaker returns dataframes since more precise tests will have to be done in test_sectionMaker'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)

        # Act
        # FIXME dependency
        hss_creator.json_to_dataframe()
        hss_creator.get_set_section()

        # Assert
        # We test that it still returns a dataframe
        for key, value in hss_creator.table_sections.items():
            assert isinstance(value, (pd.DataFrame))

    def test_fill_with_eps_data(self):
        '''tests that dataframe_to_eps_data.py to check if it returns a dataframes since more precise tests will have to be done in test_dataframe_to_eps_data'''
        # TODO test très impertinent -> il check l'init de la fonction'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)

        # Act
        # FIXME dependency
        hss_creator.json_to_dataframe()
        hss_creator.fill_with_eps_data()

        # Assert
        # We test that it still returns a dataframed
        # EPS_Data is already test covered in its own 
        assert isinstance(hss_creator.table_sections["<EPS_Data>"], pd.DataFrame)

    def test_fill_type_in_eps_data(self):
        '''checks for types sections (correct number)'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)

        # Act
        # FIXME dependency
        hss_creator.json_to_dataframe()
        hss_creator.fill_type_in_eps_data()

        # Assert
        # integrates all 4 MPs -> if all 4 MPs, there is 14 types
        for i in range(1, 14):
            assert f"Type{i}" in hss_creator.table_sections['<EPS_Data>']

    def test_convert_to_nm(self):
        # TODO
        # Arrange
        hss_creator = HssCreator(pd.DataFrame({'Move_X': [10000, 10000, 10000], 'Move_Y': [90000, 90000, 90000]}),
                                 layers=1, precision=1000)
        expected_x_in_nm = pd.Series([10000, 10000, 10000], name='Move_X')
        expected_y_in_nm = pd.Series([90000, 90000, 90000], name='Move_Y')

        # Act
        # FIXME dependency
        hss_creator.json_to_dataframe()
        hss_creator.fill_with_eps_data()
        hss_creator.convert_coord_to_nm()

        # Assert
        pd.testing.assert_series_equal(hss_creator.table_sections['<EPS_Data>']['Move_X'], expected_x_in_nm)
        pd.testing.assert_series_equal(hss_creator.table_sections['<EPS_Data>']['Move_Y'], expected_y_in_nm)

    def test_dataframe_to_hss(self):
        '''tests that the function of hss creation works and that the function of hss creation works'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)

        # Act
        # FIXME dependency
        hss_creator.json_to_dataframe()
        hss_str = hss_creator.dataframe_to_hss()

        # FIXME too fat
        expected_df_first_level_str = "<FileID>\nLIDP00\n<Version>\n6\n<Revision>\n0\n"
        expected_df_C_S_str = "<CoordinateSystem>\n#Type,ACD_Type\n1,1\n"
        expected_df_GP_C_S_str = "<GPCoordinateSystem>\n#Type\n1\n"
        expected_df_Unit_str = "<Unit>\n#Coordinate,MP_Box\n1,1\n"
        expected_df_GP_Data_str = "<GP_Data>\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT\n1,1,20,20,chef_OM_default,210,90\n"
        # FIXME beware \ at [0.0, 0.0] or a str w/ ""
        expected_df_EPS_Data_str = """<EPS_Data>\n#EPS_ID,Type1,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type2,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type3,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type4,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type5,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type6,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type7,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_X,EP_Mag_Y,EP_Rot,Type8,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type9,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type10,EP_ABCC_X,EP_ABCC_Y,Type11,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_SA_Out,MP1_MeaLeng,MP1_Direction,Type12,MP2_X,MP2_Y,MP2_Template,MP2_PNo,MP2_DNo1,MP2_DNo2,MP2_Name,MP2_TargetCD,MP2_PosOffset,MP2_SA_In,MP2_SA_Out,MP2_MeaLeng,MP2_Direction,Type13,MP3_X,MP3_Y,MP3_Template,MP3_PNo,MP3_DNo1,MP3_DNo2,MP3_Name,MP3_TargetCD,MP3_PosOffset,MP3_SA_In,MP3_SA_Out,MP3_MeaLeng,MP3_Direction,Type14,MP4_X,MP4_Y,MP4_Template,MP4_PNo,MP4_DNo1,MP4_DNo2,MP4_Name,MP4_TargetCD,MP4_PosOffset,MP4_SA_In,MP4_SA_Out,MP4_MeaLeng,MP4_Direction\n1,1,-300000000,-300000000,1,chaine,1,chaine,chaine,chaine,chaine,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,1000,1000,"[0.0, 0.0]",2,-10000,-10000,0,2,-10000,-10000,0,2,-10000,-10000,2,-300000000,-300000000,chaine,1,0,0,chaine,-200000,-200000,0,0,1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"""
        expected_df_GPA_List_str = "<GPA_List>\n#GPA_No,Chip_X,Chip_Y,GP_ID\n1,2,4,1\n2,6,4,1\n3,3,7,1\n"
        expected_df_GP_Offset_str = "<GP_Offset>\n#Offset_X,Offset_Y\n0,0\n"
        expected_df_EPA_List_str = "<EPA_List>\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode\n1,6,4,1,1\n"
        expected_df_IDD_Cond_str = """<IDD_Cond>\n#DesignData,CellName,DCRot,DCOffsetX,DCOffsetY,Tone\n,,0,0,0,0\n"""
        expected_df_IID_Layer_Data_str = """<IDD_Layer_Data>\n#LayerNo,DataType,Type,Level,DUMMY,Tone,ColorNo,FillNo,LayerName\n0,114,0,,,0,4,8,TARGET\n13,4,0,,,0,4,2,DUMMIES\n13,31,0,,,0,4,8,NOOPC\n13,100,2,,,0,13,1,SRAF\n13,0,2,,,0,4,1,OPC\n"""
        expected_df_Image_Env_str = """<ImageEnv>\n#Type,Size,CompressSW,Quality,MeasCur,CrossCur,AreaCur,DDS,MeasVal,LinePro,umMark\n0,0,0,32,0,1,0,0,0,0,0\n1,0,0,32,0,0,0,0,0,0,0\n2,0,0,32,0,0,0,0,0,0,0"""

        # Assert
        assert isinstance(hss_str, str)
        assert hss_str == expected_df_first_level_str + expected_df_C_S_str + expected_df_GP_C_S_str + expected_df_Unit_str + \
            expected_df_GP_Data_str + expected_df_EPS_Data_str + \
            expected_df_GPA_List_str + expected_df_GP_Offset_str + expected_df_EPA_List_str + expected_df_IDD_Cond_str + expected_df_IID_Layer_Data_str + expected_df_Image_Env_str

    def test_rename_eps_data_header(self):
        '''checks that the method renames "TypeN" column name in "Type"'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)
        # passes with \n
        string_to_edit = "Type1,Type12,Type100\n1,2,3\n1,2,3\n"
        expected_new_string = "Type,Type,Type\n1,2,3\n1,2,3\n"

        # Act
        new_string = hss_creator.rename_eps_data_header(string_to_edit)

        # Assert
        assert new_string == expected_new_string

    def test_set_commas_afterwards(self):
        '''checks that the method adds the correct number of commas at the end of each line'''
        # TODO check if it corresponds to correct commas number
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000)
        hss_creator.json_to_dataframe()
        string_to_modify_1 = "<GP_Data>\n" + \
            hss_creator.table_sections["<GP_Data>"].to_csv(index=False)
        expected_modified_string_1 = "<GP_Data>,,,,,,\nGP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT\n1,1,20,20,chef_OM_default,210,90\n,,,,,,\n"

        # Act
        modified_string_1 = hss_creator.set_commas_afterwards(
            string_to_modify_1)

        # Assert
        assert modified_string_1 == expected_modified_string_1

    def test_output_dataframe_to_json(self):
        # TODO change dataframe
        # Arrange
        hss_creator = HssCreator(pd.DataFrame(), layers=1, precision=1000, output_dir="/work/opc/all/users/chanelir/semrc/tests/test_output")
        hss_creator.constant_sections = {'<FileID>': 'LIDP00', '<Version>': 6, '<Revision>': 0}
        hss_creator.table_sections = {
            '<CoordinateSystem>': pd.DataFrame([{'Type': 1, 'ACD_Type': 1}]),
            '<Unit>': pd.DataFrame([{'Coordinate': 1, 'MP_Box': 1}])
        }

        expected_json_content = {
            '<FileID>': 'LIDP00',
            '<Version>': 6,
            '<Revision>': 0,
            '<CoordinateSystem>': {
                'Type': 1,
                'ACD_Type': 1},
            '<Unit>': {
                'Coordinate': 1,
                'MP_Box': 1}
        }
        expected_json_str = json.dumps(expected_json_content, indent=4)

        # Act
        hss_creator.output_dataframe_to_json()
        with open(str(hss_creator.recipe_output_file) + ".json", 'r') as json_file:
            content = json_file.read()

        # Assert
        assert os.path.exists(str(hss_creator.recipe_output_file) + ".json")
        assert content == expected_json_str

    def test_write_in_file(self):
        '''checks for file writing and content written'''
        # TODO this test is dependent from "OM" or "SEM" type of measure
        # TODO must test the correct execution of several method
        # -> method are already tested / output is a way to validate it

        # Arrange
        test_tmp_path = Path(__file__).resolve().parent
        recipe_name = "test_temp_output"
        output_recipe_file_path = Path(test_tmp_path / (recipe_name + ".csv"))
        output_json_file_path = Path(test_tmp_path / (recipe_name + ".json"))
        example_test_df_genepy_gauge = pd.DataFrame({
            'EPS_Name': ['isoRectArea_CD100_Area6000_V', 'isoRectArea_CD200_Area6000_V', 'isoRectArea_CD300_Area6000_V', 'isoRectArea_CD400_Area6000_V', 'isoRectArea_CD500_Area6000_V', 'isoRectArea_CD600_Area6000_V', 'isoRectArea_CD700_Area6000_V', 'isoRectArea_CD800_Area6000_V', 'isoRectArea_CD900_Area6000_V', 'isoRectArea_CD1000_Area6000_V'],
            'Move_X': [55000, 110000, 165000, 220000, 275000, 330000, 385000, 440000, 495000, 550000],
            'Move_Y': [-455000, -455000, -455000, -455000, -455000, -455000, -455000, -455000, -455000, -455000],
            'EPS_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            })

        hss_creator = HssCreator(example_test_df_genepy_gauge, layers=1, output_dir=test_tmp_path,
                                 recipe_name=recipe_name, layout=LAYOUT_TESTCASE,
                                 topcell="OPCfield", precision=1000)

        # Act
        hss_creator.write_in_file()

        assert test_tmp_path.exists(), "The file does not exist."
        with open(hss_creator.recipe_output_file.with_suffix(".csv"), 'r') as file:
            content = file.read()
            assert content, "The file is empty."
        output_recipe_file_path.unlink()
        output_json_file_path.unlink()
