import pytest
import pathlib
import pandas as pd
# from unittest.mock import MagicMock
from app.hss_modules.hss_creator import HssCreator

# TODO make relative file path for "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"

# FIXME les colonnes nécessaire au fonctionnement du test seulement
# test les vrai fonctions et 1 chose à la fois -> sinon fonction est mal écrite

# in creation of HssCreator() class, template argument should be empty the check if expected_data == template set in __init__ of the class


class TestHssCreator:

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
                "GP_Template": "",
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
                "EP_Mag_Scan_X": 1000,
                "EP_Mag_Scan_Y": 1000,
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
                "MP1_Cursor_Size_X": 0,
                "MP1_SA_Out": 0,
                "MP1_Cursor_Size_Y": 0,
                "MP1_MeaLeng": 1,
                "MP1_Direction": 1
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
                "Chip_X": 1,
                "Chip_Y": 1,
                "EPS_ID": 1,
                "Move_Mode": 1
            }
        }

        # Act
        hss_creator = HssCreator(pd.DataFrame)
        actual_json_output = hss_creator.json_template

        # Assert
        # TODO not sure about the error raised
        if actual_json_output != expected_output:
            raise FileNotFoundError("File may not be in expected directory")
        assert actual_json_output == expected_output

    def test_json_to_dataframe(self):
        '''tests that the template is correctly generated in several dataframes'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())

        # Act
        hss_creator.json_to_dataframe()

        # Assert
        # Assert first_level_df
        expected_first_level_df = pd.DataFrame({
            "<FileID>": ["LIDP00"],
            "<Version>": [6],
            "<Revision>": [0]
        })
        assert hss_creator.constant_sections.equals(expected_first_level_df)

        # Assert <CoordinateSystem>
        expected_coordinate_system = pd.DataFrame(
            {"Type": [1], "ACD_Type": [1]})
        assert hss_creator.table_sections["<CoordinateSystem>"].equals(
            expected_coordinate_system)

        # Assert <GPCoordinateSystem>
        expected_gp_coordinate_system = pd.DataFrame({"Type": [1]})
        assert hss_creator.table_sections["<GPCoordinateSystem>"].equals(
            expected_gp_coordinate_system)

        # Assert <Unit>
        expected_unit = pd.DataFrame({"Coordinate": [1], "MP_Box": [1]})
        assert hss_creator.table_sections["<Unit>"].equals(
            expected_unit)

        # Assert <GP_Data>
        expected_gp_data = pd.DataFrame({
            "GP_ID": [1],
            "Type": [1],
            "GP_X": [20],
            "GP_Y": [20],
            "GP_Template": [""],
            "GP_MAG": [210],
            "GP_ROT": [90]
        })
        assert hss_creator.table_sections["<GP_Data>"].equals(
            expected_gp_data)

        # Assert <EPS_Data>
        expected_eps_data = pd.DataFrame({
            "EPS_ID": [1],
            "Type1": [1],
            "Move_X": [-300000000],
            "Move_Y": [-300000000],
            "Mode": [1],
            "EPS_Name": ["chaine"],
            "Ref_EPS_ID": [1],
            "EPS_Template": ["chaine"],
            "AP1_Template": ["chaine"],
            "AP2_Template": ["chaine"],
            "EP_Template": ["chaine"],
            "Type2": [2],
            "AP1_X": [-300000000],
            "AP1_Y": [-300000000],
            "AP1_Mag": [1000],
            "AP1_Rot": [0],
            "Type3": [2],
            "AP1_AF_X": [-300000000],
            "AP1_AF_Y": [-300000000],
            "AP1_AF_Mag": [0],
            "Type4": [2],
            "AP1_AST_X": [-300000000],
            "AP1_AST_Y": [-300000000],
            "AP1_AST_Mag": [0],
            "Type5": [2],
            "AP2_X": [-300000000],
            "AP2_Y": [-300000000],
            "AP2_Mag": [1000],
            "AP2_Rot": [0],
            "Type6": [2],
            "AP2_AF_X": [-300000000],
            "AP2_AF_Y": [-300000000],
            "AP2_AF_Mag": [0],
            "Type7": [2],
            "AP2_AST_X": [-300000000],
            "AP2_AST_Y": [-300000000],
            "AP2_AST_Mag": [0],
            "EP_Mag_Scan_X": [1000],
            "EP_Mag_Scan_Y": [1000],
            "EP_Rot": [[0.0, 0.0]],
            "Type8": [2],
            "EP_AF_X": [-10000],
            "EP_AF_Y": [-10000],
            "EP_AF_Mag": [0],
            "Type9": [2],
            "EP_AST_X": [-10000],
            "EP_AST_Y": [-10000],
            "EP_AST_Mag": [0],
            "Type10": [2],
            "EP_ABCC_X": [-10000],
            "EP_ABCC_Y": [-10000],
            "Type11": [2],
            "MP1_X": [-300000000],
            "MP1_Y": [-300000000],
            "MP1_Template": ["chaine"],
            "MP1_PNo": [1],
            "MP1_DNo1": [0],
            "MP1_DNo2": [0],
            "MP1_Name": ["chaine"],
            "MP1_TargetCD": [-200000],
            "MP1_PosOffset": [-200000],
            "MP1_SA_In": [0],
            "MP1_Cursor_Size_X": [0],
            "MP1_SA_Out": [0],
            "MP1_Cursor_Size_Y": [0],
            "MP1_MeaLeng": [1],
            "MP1_Direction": [1]
        })
        assert hss_creator.table_sections["<EPS_Data>"].equals(
            expected_eps_data)

        # Assert <GPA_List>
        expected_gpa_list = pd.DataFrame({
            "GPA_No": [1, 2, 3],
            "Chip_X": [2, 6, 3],
            "Chip_Y": [4, 4, 7],
            "GP_ID": [1, 1, 1]
        })
        assert hss_creator.table_sections["<GPA_List>"].equals(
            expected_gpa_list)

        # Assert <GP_Offset>
        expected_gp_offset = pd.DataFrame({"Offset_X": [0], "Offset_Y": [0]})
        assert hss_creator.table_sections["<GP_Offset>"].equals(
            expected_gp_offset)

        # Assert <EPA_List>
        expected_epa_list = pd.DataFrame({
            "EPA_No": [1],
            "Chip_X": [1],
            "Chip_Y": [1],
            "EPS_ID": [1],
            "Move_Mode": [1]
        })
        assert hss_creator.table_sections["<EPA_List>"].equals(
            expected_epa_list)

    def test_get_set_section(self):
        '''tests that sectionMaker returns dataframes since more precise tests will have to be done in test_sectionMaker'''
        # TODO test très impertinent -> il check l'init de la fonction
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())

        # Act
        # hss_creator.json_to_dataframe()
        hss_creator.get_set_section()

        # Assert
        # We test that it still returns a dataframe
        for key, value in hss_creator.table_sections.items():
            assert isinstance(value, pd.DataFrame)

    def test_add_MP(self):
        '''tests the correct adding of MP'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())

        # Act
        hss_creator.json_to_dataframe()
        hss_creator.add_MP(2)

        expected_eps_data = pd.DataFrame({
            "EPS_ID": [1],
            "Type1": [1],
            "Move_X": [-300000000],
            "Move_Y": [-300000000],
            "Mode": [1],
            "EPS_Name": ["chaine"],
            "Ref_EPS_ID": [1],
            "EPS_Template": ["chaine"],
            "AP1_Template": ["chaine"],
            "AP2_Template": ["chaine"],
            "EP_Template": ["chaine"],
            "Type2": [2],
            "AP1_X": [-300000000],
            "AP1_Y": [-300000000],
            "AP1_Mag": [1000],
            "AP1_Rot": [0],
            "Type3": [2],
            "AP1_AF_X": [-300000000],
            "AP1_AF_Y": [-300000000],
            "AP1_AF_Mag": [0],
            "Type4": [2],
            "AP1_AST_X": [-300000000],
            "AP1_AST_Y": [-300000000],
            "AP1_AST_Mag": [0],
            "Type5": [2],
            "AP2_X": [-300000000],
            "AP2_Y": [-300000000],
            "AP2_Mag": [1000],
            "AP2_Rot": [0],
            "Type6": [2],
            "AP2_AF_X": [-300000000],
            "AP2_AF_Y": [-300000000],
            "AP2_AF_Mag": [0],
            "Type7": [2],
            "AP2_AST_X": [-300000000],
            "AP2_AST_Y": [-300000000],
            "AP2_AST_Mag": [0],
            "EP_Mag_Scan_X": [1000],
            "EP_Mag_Scan_Y": [1000],
            "EP_Rot": [[0.0, 0.0]],
            "Type8": [2],
            "EP_AF_X": [-10000],
            "EP_AF_Y": [-10000],
            "EP_AF_Mag": [0],
            "Type9": [2],
            "EP_AST_X": [-10000],
            "EP_AST_Y": [-10000],
            "EP_AST_Mag": [0],
            "Type10": [2],
            "EP_ABCC_X": [-10000],
            "EP_ABCC_Y": [-10000],
            "Type11": [2],
            "MP1_X": [-300000000],
            "MP1_Y": [-300000000],
            "MP1_Template": ["chaine"],
            "MP1_PNo": [1],
            "MP1_DNo1": [0],
            "MP1_DNo2": [0],
            "MP1_Name": ["chaine"],
            "MP1_TargetCD": [-200000],
            "MP1_PosOffset": [-200000],
            "MP1_SA_In": [0],
            "MP1_Cursor_Size_X": [0],
            "MP1_SA_Out": [0],
            "MP1_Cursor_Size_Y": [0],
            "MP1_MeaLeng": [1],
            "MP1_Direction": [1],
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
            "MP2_Cursor_Size_X": "",
            "MP2_SA_Out": "",
            "MP2_Cursor_Size_Y": "",
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
            "MP3_Cursor_Size_X": "",
            "MP3_SA_Out": "",
            "MP3_Cursor_Size_Y": "",
            "MP3_MeaLeng": "",
            "MP3_Direction": ""
        })

        # Assert
        # FIXME maybe we would like to check all the data
        assert hss_creator.table_sections["<EPS_Data>"].columns.equals(
            expected_eps_data.columns)

    def test_fill_with_eps_data(self):
        '''tests that dataframe_to_eps_data.py to check if it returns a dataframes since more precise tests will have to be done in test_dataframe_to_eps_data'''
        # TODO test très impertinent -> il check l'init de la fonction'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())

        # Act
        hss_creator.json_to_dataframe()
        hss_creator.fill_with_eps_data()

        # Assert
        # We test that it still returns a dataframe
        assert isinstance(
            hss_creator.table_sections["<EPS_Data>"], pd.DataFrame)

    def test_fill_type_in_eps_data(self):
        '''checks for types sections (correct number)'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())

        # TODO tester pour le cas d'un ajout d'MP ?

        expected_eps_data_df = pd.DataFrame({
            "EPS_ID": [1],
            "Type1": [1],
            "Move_X": [-300000000],
            "Move_Y": [-300000000],
            "Mode": [1],
            "EPS_Name": ["chaine"],
            "Ref_EPS_ID": [1],
            "EPS_Template": ["chaine"],
            "AP1_Template": ["chaine"],
            "AP2_Template": ["chaine"],
            "EP_Template": ["chaine"],
            "Type2": [2],
            "AP1_X": [-300000000],
            "AP1_Y": [-300000000],
            "AP1_Mag": [1000],
            "AP1_Rot": [0],
            "Type3": [2],
            "AP1_AF_X": [-300000000],
            "AP1_AF_Y": [-300000000],
            "AP1_AF_Mag": [0],
            "Type4": [2],
            "AP1_AST_X": [-300000000],
            "AP1_AST_Y": [-300000000],
            "AP1_AST_Mag": [0],
            "Type5": [2],
            "AP2_X": [-300000000],
            "AP2_Y": [-300000000],
            "AP2_Mag": [1000],
            "AP2_Rot": [0],
            "Type6": [2],
            "AP2_AF_X": [-300000000],
            "AP2_AF_Y": [-300000000],
            "AP2_AF_Mag": [0],
            "Type7": [2],
            "AP2_AST_X": [-300000000],
            "AP2_AST_Y": [-300000000],
            "AP2_AST_Mag": [0],
            "EP_Mag_Scan_X": [1000],
            "EP_Mag_Scan_Y": [1000],
            "EP_Rot": [[0.0, 0.0]],
            "Type8": [2],
            "EP_AF_X": [-10000],
            "EP_AF_Y": [-10000],
            "EP_AF_Mag": [0],
            "Type9": [2],
            "EP_AST_X": [-10000],
            "EP_AST_Y": [-10000],
            "EP_AST_Mag": [0],
            "Type10": [2],
            "EP_ABCC_X": [-10000],
            "EP_ABCC_Y": [-10000],
            "Type11": [2],
            "MP1_X": [-300000000],
            "MP1_Y": [-300000000],
            "MP1_Template": ["chaine"],
            "MP1_PNo": [1],
            "MP1_DNo1": [0],
            "MP1_DNo2": [0],
            "MP1_Name": ["chaine"],
            "MP1_TargetCD": [-200000],
            "MP1_PosOffset": [-200000],
            "MP1_SA_In": [0],
            "MP1_Cursor_Size_X": [0],
            "MP1_SA_Out": [0],
            "MP1_Cursor_Size_Y": [0],
            "MP1_MeaLeng": [1],
            "MP1_Direction": [1]
        })

        # Act
        hss_creator.json_to_dataframe()
        hss_creator.fill_type_in_eps_data(1)

        # Assert
        pd.testing.assert_frame_equal(
            hss_creator.table_sections["<EPS_Data>"], expected_eps_data_df)

    def test_dataframe_to_hss(self):
        '''tests that the function of hss creation works and that the function of hss creation works'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())

        # Act
        hss_creator.json_to_dataframe()
        hss_str = hss_creator.dataframe_to_hss()

        # Assert
        expected_df_first_level_str = "<FileID>\nLIDP00\n<Version>\n6\n<Revision>\n0\n"
        expected_df_C_S_str = "<CoordinateSystem>\n#Type,ACD_Type\n1,1\n"
        expected_df_GP_C_S_str = "<GPCoordinateSystem>\n#Type\n1\n"
        expected_df_Unit_str = "<Unit>\n#Coordinate,MP_Box\n1,1\n"
        expected_df_GP_Data_str = "<GP_Data>\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT\n1,1,20,20,,210,90\n"
        # FIXME beware \ at [0.0, 0.0] or a str w/ ""
        expected_df_EPS_Data_str = """<EPS_Data>\n#EPS_ID,Type1,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type2,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type3,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type4,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type5,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type6,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type7,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_Scan_X,EP_Mag_Scan_Y,EP_Rot,Type8,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type9,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type10,EP_ABCC_X,EP_ABCC_Y,Type11,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_Cursor_Size_X,MP1_SA_Out,MP1_Cursor_Size_Y,MP1_MeaLeng,MP1_Direction\n1,1,-300000000,-300000000,1,chaine,1,chaine,chaine,chaine,chaine,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,1000,1000,"[0.0, 0.0]",2,-10000,-10000,0,2,-10000,-10000,0,2,-10000,-10000,2,-300000000,-300000000,chaine,1,0,0,chaine,-200000,-200000,0,0,0,0,1,1\n"""
        expected_df_GPA_List_str = "<GPA_List>\n#GPA_No,Chip_X,Chip_Y,GP_ID\n1,2,4,1\n2,6,4,1\n3,3,7,1\n"
        expected_df_GP_Offset_str = "<GP_Offset>\n#Offset_X,Offset_Y\n0,0\n"
        expected_df_EPA_List_str = "<EPA_List>\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode\n1,1,1,1,1"

        assert hss_str == expected_df_first_level_str + expected_df_C_S_str + expected_df_GP_C_S_str + expected_df_Unit_str + \
            expected_df_GP_Data_str + expected_df_EPS_Data_str + \
            expected_df_GPA_List_str + expected_df_GP_Offset_str + expected_df_EPA_List_str

    def test_rename_eps_data_header(self):
        '''checks that the method renames "TypeN" column name in "Type"'''
        # Arrange
        hss_creator = HssCreator(pd.DataFrame())
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
        hss_creator = HssCreator(pd.DataFrame())
        hss_creator.json_to_dataframe()
        string_to_modify_1 = "<GP_Data>\n" + \
            hss_creator.table_sections["<GP_Data>"].to_csv(
                index=False)
        expected_modified_string_1 = "<GP_Data>,,,,,,\nGP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT\n1,1,20,20,,210,90\n,,,,,,\n"

        # Act
        modified_string_1 = hss_creator.set_commas_afterwards(
            string_to_modify_1)

        # Assert
        assert modified_string_1 == expected_modified_string_1

    def test_write_in_file(self):
        '''checks for file writing and content written'''
        # TODO this test is dependent from "OM" or "SEM" type of measure
        # Arrange
        test_tmp_path = pathlib.Path(__file__).resolve().parent / "test_temp_output.hss"
        example_test_df_genepy_gauge = pd.DataFrame({'EPS_Name': ['isoRectArea_CD100_Area6000_V', 'isoRectArea_CD200_Area6000_V', 'isoRectArea_CD300_Area6000_V', 'isoRectArea_CD400_Area6000_V', 'isoRectArea_CD500_Area6000_V', 'isoRectArea_CD600_Area6000_V', 'isoRectArea_CD700_Area6000_V', 'isoRectArea_CD800_Area6000_V', 'isoRectArea_CD900_Area6000_V', 'isoRectArea_CD1000_Area6000_V'],
                                                     'Move_X': [55000, 110000, 165000, 220000, 275000, 330000, 385000, 440000, 495000, 550000],
                                                     'Move_Y': [-455000, -455000, -455000, -455000, -455000, -455000, -455000, -455000, -455000, -455000],
                                                     'MP_TargetCD': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                                     'EPS_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})

        hss_creator = HssCreator(example_test_df_genepy_gauge, output_file=test_tmp_path)
        # TODO handle false result when df is empty
        # hss_creator = HssCreator(pd.DataFrame(), template=test_json_template, output_file=test_tmp_path)

        # Act
        hss_creator.write_in_file(0)

        # Assert
        with open(test_tmp_path, 'r') as f:
            hss_str = f.read()
        expected_hss_str = """<FileID>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\nLIDP00,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Version>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n6,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Revision>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<CoordinateSystem>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Type,ACD_Type,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GPCoordinateSystem>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Type,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Unit>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Coordinate,MP_Box,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GP_Data>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,20,20,chef_OM_default,104,90,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<EPS_Data>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#EPS_ID,Type,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_Scan_X,EP_Mag_Scan_Y,EP_Rot,Type,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type,EP_ABCC_X,EP_ABCC_Y,Type,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_Cursor_Size_X,MP1_SA_Out,MP1_Cursor_Size_Y,MP1_MeaLeng,MP1_Direction\n1,1,55000,-455000,,isoRectArea_CD100_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n2,1,110000,-455000,,isoRectArea_CD200_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n3,1,165000,-455000,,isoRectArea_CD300_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n4,1,220000,-455000,,isoRectArea_CD400_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n5,1,275000,-455000,,isoRectArea_CD500_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n6,1,330000,-455000,,isoRectArea_CD600_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n7,1,385000,-455000,,isoRectArea_CD700_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n8,1,440000,-455000,,isoRectArea_CD800_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n9,1,495000,-455000,,isoRectArea_CD900_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n10,1,550000,-455000,,isoRectArea_CD1000_Area6000_V,,,,,,2,,,,,2,,,,2,,,,2,,,,,2,,,,2,,,,,,,2,,,,2,,,,2,,,,,,,,,,,,,,,,,,\n<GPA_List>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#GPA_No,Chip_X,Chip_Y,GP_ID,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,2,4,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n2,6,4,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n3,3,7,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GP_Offset>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Offset_X,Offset_Y,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<EPA_List>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,1,1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"""

        assert hss_str == expected_hss_str
