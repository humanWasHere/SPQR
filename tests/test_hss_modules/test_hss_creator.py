import pandas as pd
import json
# from unittest.mock import MagicMock
from app.hss_modules.hss_creator import HssCreator

# TODO make relative file path for "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"


class TestHssCreator:

    def test_import_json(self):
        '''checks that the template is correclty imported as a file'''
        # Arrange
        test_file_path = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
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

        # Create a test JSON file
        with open(test_file_path, "w") as f:
            json.dump(expected_output, f)

        # Act
        hss_creator = HssCreator(
            eps_dataframe=None, template=test_file_path, output_file=None)
        actual_output = hss_creator.json_template

        # Assert
        # TODO not sure about the error raised
        if actual_output != expected_output:
            raise FileNotFoundError("File may not be in expected directory")
        assert actual_output == expected_output

    def test_json_to_dataframe(self):
        '''tests that the template is correctly generated into a dataframe'''
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)

        # Act
        hss_creator.json_to_dataframe()

        # Assert
        # test template content as df
        # Assert first_level_df
        expected_first_level_df = pd.DataFrame({
            "<FileID>": ["LIDP00"],
            "<Version>": [6],
            "<Revision>": [0]
        })
        assert hss_creator.first_level_df.equals(expected_first_level_df)

        # Assert <CoordinateSystem>
        expected_coordinate_system = pd.DataFrame(
            {"Type": [1], "ACD_Type": [1]})
        assert hss_creator.dict_of_second_level_df["<CoordinateSystem>"].equals(
            expected_coordinate_system)

        # Assert <GPCoordinateSystem>
        expected_gp_coordinate_system = pd.DataFrame({"Type": [1]})
        assert hss_creator.dict_of_second_level_df["<GPCoordinateSystem>"].equals(
            expected_gp_coordinate_system)

        # Assert <Unit>
        expected_unit = pd.DataFrame({"Coordinate": [1], "MP_Box": [1]})
        assert hss_creator.dict_of_second_level_df["<Unit>"].equals(
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
        assert hss_creator.dict_of_second_level_df["<GP_Data>"].equals(
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
        assert hss_creator.dict_of_second_level_df["<EPS_Data>"].equals(
            expected_eps_data)

        # Assert <GPA_List>
        expected_gpa_list = pd.DataFrame({
            "GPA_No": [1, 2, 3],
            "Chip_X": [2, 6, 3],
            "Chip_Y": [4, 4, 7],
            "GP_ID": [1, 1, 1]
        })
        assert hss_creator.dict_of_second_level_df["<GPA_List>"].equals(
            expected_gpa_list)

        # Assert <GP_Offset>
        expected_gp_offset = pd.DataFrame({"Offset_X": [0], "Offset_Y": [0]})
        assert hss_creator.dict_of_second_level_df["<GP_Offset>"].equals(
            expected_gp_offset)

        # Assert <EPA_List>
        expected_epa_list = pd.DataFrame({
            "EPA_No": [1],
            "Chip_X": [1],
            "Chip_Y": [1],
            "EPS_ID": [1],
            "Move_Mode": [1]
        })
        assert hss_creator.dict_of_second_level_df["<EPA_List>"].equals(
            expected_epa_list)

        # TODO raise a ValueError for template change

    def test_get_set_section(self):
        '''tests that sectionMaker returns dataframes'''
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)

        # Act
        hss_creator.json_to_dataframe()
        hss_creator.get_set_section()

        # Assert
        # We test that it still returns a dataframe
        for key, value in hss_creator.dict_of_second_level_df.items():
            assert isinstance(value, pd.DataFrame)

    # FIXME this test fails
    def test_add_MP(self):
        '''tests the correct adding of MP'''
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)

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
        # assert hss_creator.dict_of_second_level_df["<EPS_Data>"].equals(
        #     pd.DataFrame(columns=list(expected_eps_data.columns.values)))
        assert hss_creator.dict_of_second_level_df["<EPS_Data>"].columns.equals(
            expected_eps_data.columns)

    def test_fill_with_eps_data(self):
        '''tests that dataframe_to_eps_data.py to check if it returns a dataframes'''
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)

        # Act
        hss_creator.json_to_dataframe()
        hss_creator.fill_with_eps_data()

        # Assert
        # We test that it still returns a dataframe
        assert isinstance(
            hss_creator.dict_of_second_level_df["<EPS_Data>"], pd.DataFrame)

    def test_fill_type_in_eps_data(self):
        '''checks for types sections (correct number)'''
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)

        # TODO ajouter dans le cas d'un ajout d'MP ?
        # TODO avec un index seulement ? -> call fill_with_eps_data() ?

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

        # expected_eps_data_df_2 = pd.DataFrame({
        #     "EPS_ID": [1],
        #     "Type1": [1],
        #     "Move_X": [-300000000],
        #     "Move_Y": [-300000000],
        #     "Mode": [1],
        #     "EPS_Name": ["chaine"],
        #     "Ref_EPS_ID": [1],
        #     "EPS_Template": ["chaine"],
        #     "AP1_Template": ["chaine"],
        #     "AP2_Template": ["chaine"],
        #     "EP_Template": ["chaine"],
        #     "Type2": [2],
        #     "AP1_X": [-300000000],
        #     "AP1_Y": [-300000000],
        #     "AP1_Mag": [1000],
        #     "AP1_Rot": [0],
        #     "Type3": [2],
        #     "AP1_AF_X": [-300000000],
        #     "AP1_AF_Y": [-300000000],
        #     "AP1_AF_Mag": [0],
        #     "Type4": [2],
        #     "AP1_AST_X": [-300000000],
        #     "AP1_AST_Y": [-300000000],
        #     "AP1_AST_Mag": [0],
        #     "Type5": [2],
        #     "AP2_X": [-300000000],
        #     "AP2_Y": [-300000000],
        #     "AP2_Mag": [1000],
        #     "AP2_Rot": [0],
        #     "Type6": [2],
        #     "AP2_AF_X": [-300000000],
        #     "AP2_AF_Y": [-300000000],
        #     "AP2_AF_Mag": [0],
        #     "Type7": [2],
        #     "AP2_AST_X": [-300000000],
        #     "AP2_AST_Y": [-300000000],
        #     "AP2_AST_Mag": [0],
        #     "EP_Mag_Scan_X": [1000],
        #     "EP_Mag_Scan_Y": [1000],
        #     "EP_Rot": [[0.0, 0.0]],
        #     "Type8": [2],
        #     "EP_AF_X": [-10000],
        #     "EP_AF_Y": [-10000],
        #     "EP_AF_Mag": [0],
        #     "Type9": [2],
        #     "EP_AST_X": [-10000],
        #     "EP_AST_Y": [-10000],
        #     "EP_AST_Mag": [0],
        #     "Type10": [2],
        #     "EP_ABCC_X": [-10000],
        #     "EP_ABCC_Y": [-10000],
        #     "Type11": [2],
        #     "MP1_X": [-300000000],
        #     "MP1_Y": [-300000000],
        #     "MP1_Template": ["chaine"],
        #     "MP1_PNo": [1],
        #     "MP1_DNo1": [0],
        #     "MP1_DNo2": [0],
        #     "MP1_Name": ["chaine"],
        #     "MP1_TargetCD": [-200000],
        #     "MP1_PosOffset": [-200000],
        #     "MP1_SA_In": [0],
        #     "MP1_Cursor_Size_X": [0],
        #     "MP1_SA_Out": [0],
        #     "MP1_Cursor_Size_Y": [0],
        #     "MP1_MeaLeng": [1],
        #     "MP1_Direction": [1],
        #     "Type12": [2],
        #     "MP2_X": [-300000000],
        #     "MP2_Y": [-300000000],
        #     "MP2_Template": ["chaine"],
        #     "MP2_PNo": [1],
        #     "MP2_DNo1": [0],
        #     "MP2_DNo2": [0],
        #     "MP2_Name": ["chaine"],
        #     "MP2_TargetCD": [-200000],
        #     "MP2_PosOffset": [-200000],
        #     "MP2_SA_In": [0],
        #     "MP2_Cursor_Size_X": [0],
        #     "MP2_SA_Out": [0],
        #     "MP2_Cursor_Size_Y": [0],
        #     "MP2_MeaLeng": [1],
        #     "MP2_Direction": [1]
        # })

        # expected_eps_data_df_3 = pd.DataFrame({
        #     "EPS_ID": [1],
        #     "Type1": [1],
        #     "Move_X": [-300000000],
        #     "Move_Y": [-300000000],
        #     "Mode": [1],
        #     "EPS_Name": ["chaine"],
        #     "Ref_EPS_ID": [1],
        #     "EPS_Template": ["chaine"],
        #     "AP1_Template": ["chaine"],
        #     "AP2_Template": ["chaine"],
        #     "EP_Template": ["chaine"],
        #     "Type2": [2],
        #     "AP1_X": [-300000000],
        #     "AP1_Y": [-300000000],
        #     "AP1_Mag": [1000],
        #     "AP1_Rot": [0],
        #     "Type3": [2],
        #     "AP1_AF_X": [-300000000],
        #     "AP1_AF_Y": [-300000000],
        #     "AP1_AF_Mag": [0],
        #     "Type4": [2],
        #     "AP1_AST_X": [-300000000],
        #     "AP1_AST_Y": [-300000000],
        #     "AP1_AST_Mag": [0],
        #     "Type5": [2],
        #     "AP2_X": [-300000000],
        #     "AP2_Y": [-300000000],
        #     "AP2_Mag": [1000],
        #     "AP2_Rot": [0],
        #     "Type6": [2],
        #     "AP2_AF_X": [-300000000],
        #     "AP2_AF_Y": [-300000000],
        #     "AP2_AF_Mag": [0],
        #     "Type7": [2],
        #     "AP2_AST_X": [-300000000],
        #     "AP2_AST_Y": [-300000000],
        #     "AP2_AST_Mag": [0],
        #     "EP_Mag_Scan_X": [1000],
        #     "EP_Mag_Scan_Y": [1000],
        #     "EP_Rot": [[0.0, 0.0]],
        #     "Type8": [2],
        #     "EP_AF_X": [-10000],
        #     "EP_AF_Y": [-10000],
        #     "EP_AF_Mag": [0],
        #     "Type9": [2],
        #     "EP_AST_X": [-10000],
        #     "EP_AST_Y": [-10000],
        #     "EP_AST_Mag": [0],
        #     "Type10": [2],
        #     "EP_ABCC_X": [-10000],
        #     "EP_ABCC_Y": [-10000],
        #     "Type11": "",
        #     "MP1_X": "",
        #     "MP1_Y": "",
        #     "MP1_Template": "",
        #     "MP1_PNo": "",
        #     "MP1_DNo1": "",
        #     "MP1_DNo2": "",
        #     "MP1_Name": "",
        #     "MP1_TargetCD": "",
        #     "MP1_PosOffset": "",
        #     "MP1_SA_In": "",
        #     "MP1_Cursor_Size_X": "",
        #     "MP1_SA_Out": "",
        #     "MP1_Cursor_Size_Y": "",
        #     "MP1_MeaLeng": "",
        #     "MP1_Direction": ""
        # })

        # expected_eps_data_df_4 = pd.DataFrame({
        #     "EPS_ID": [1],
        #     "Type1": [1],
        #     "Move_X": [-300000000],
        #     "Move_Y": [-300000000],
        #     "Mode": [1],
        #     "EPS_Name": ["chaine"],
        #     "Ref_EPS_ID": [1],
        #     "EPS_Template": ["chaine"],
        #     "AP1_Template": ["chaine"],
        #     "AP2_Template": ["chaine"],
        #     "EP_Template": ["chaine"],
        #     "Type2": [2],
        #     "AP1_X": [-300000000],
        #     "AP1_Y": [-300000000],
        #     "AP1_Mag": [1000],
        #     "AP1_Rot": [0],
        #     "Type3": [2],
        #     "AP1_AF_X": [-300000000],
        #     "AP1_AF_Y": [-300000000],
        #     "AP1_AF_Mag": [0],
        #     "Type4": [2],
        #     "AP1_AST_X": [-300000000],
        #     "AP1_AST_Y": [-300000000],
        #     "AP1_AST_Mag": [0],
        #     "Type5": [2],
        #     "AP2_X": [-300000000],
        #     "AP2_Y": [-300000000],
        #     "AP2_Mag": [1000],
        #     "AP2_Rot": [0],
        #     "Type6": [2],
        #     "AP2_AF_X": [-300000000],
        #     "AP2_AF_Y": [-300000000],
        #     "AP2_AF_Mag": [0],
        #     "Type7": [2],
        #     "AP2_AST_X": [-300000000],
        #     "AP2_AST_Y": [-300000000],
        #     "AP2_AST_Mag": [0],
        #     "EP_Mag_Scan_X": [1000],
        #     "EP_Mag_Scan_Y": [1000],
        #     "EP_Rot": [[0.0, 0.0]],
        #     "Type8": [2],
        #     "EP_AF_X": [-10000],
        #     "EP_AF_Y": [-10000],
        #     "EP_AF_Mag": [0],
        #     "Type9": [2],
        #     "EP_AST_X": [-10000],
        #     "EP_AST_Y": [-10000],
        #     "EP_AST_Mag": [0],
        #     "Type10": [2],
        #     "EP_ABCC_X": [-10000],
        #     "EP_ABCC_Y": [-10000],
        #     "Type11": [],
        #     "MP1_X": [],
        #     "MP1_Y": [],
        #     "MP1_Template": [],
        #     "MP1_PNo": [],
        #     "MP1_DNo1": [],
        #     "MP1_DNo2": [],
        #     "MP1_Name": [],
        #     "MP1_TargetCD": [],
        #     "MP1_PosOffset": [],
        #     "MP1_SA_In": [],
        #     "MP1_Cursor_Size_X": [],
        #     "MP1_SA_Out": [],
        #     "MP1_Cursor_Size_Y": [],
        #     "MP1_MeaLeng": [],
        #     "MP1_Direction": []
        # })

        # Act
        hss_creator.json_to_dataframe()
        hss_creator.fill_type_in_eps_data(1)

        # Assert
        # assert hss_creator.dict_of_second_level_df["<EPS_Data>"] == expected_eps_data_df

        pd.testing.assert_frame_equal(
            hss_creator.dict_of_second_level_df["<EPS_Data>"], expected_eps_data_df)
        # should not pass - aka Gandalf testing
        # pd.testing.assert_frame_equal(hss_creator.dict_of_second_level_df["<EPS_Data>"], expected_eps_data_df_2)
        # pd.testing.assert_frame_equal(hss_creator.dict_of_second_level_df["<EPS_Data>"], expected_eps_data_df_3)
        # pd.testing.assert_frame_equal(hss_creator.dict_of_second_level_df["<EPS_Data>"], expected_eps_data_df_4)

    def test_dataframe_to_hss(self):
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)

        # Act
        hss_creator.json_to_dataframe()
        hss_str = hss_creator.dataframe_to_hss()

        # Assert
        # FIXME str ?
        expected_df_first_level_str = str(
            "<FileID>\nLIDP00\n<Version>\n6\n<Revision>\n0\n")
        expected_df_C_S_str = str("<CoordinateSystem>\n#Type,ACD_Type\n1,1\n")
        expected_df_GP_C_S_str = str("<GPCoordinateSystem>\n#Type\n1\n")
        expected_df_Unit_str = str("<Unit>\n#Coordinate,MP_Box\n1,1\n")
        expected_df_GP_Data_str = str(
            "<GP_Data>\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT\n1,1,20,20,,210,90\n")
        # FIXME beware \ at [0.0, 0.0] or a str w/ ""
        expected_df_EPS_Data_str = str(
            """<EPS_Data>\n#EPS_ID,Type1,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type2,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type3,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type4,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type5,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type6,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type7,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_Scan_X,EP_Mag_Scan_Y,EP_Rot,Type8,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type9,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type10,EP_ABCC_X,EP_ABCC_Y,Type11,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_Cursor_Size_X,MP1_SA_Out,MP1_Cursor_Size_Y,MP1_MeaLeng,MP1_Direction\n1,1,-300000000,-300000000,1,chaine,1,chaine,chaine,chaine,chaine,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,1000,1000,"[0.0, 0.0]",2,-10000,-10000,0,2,-10000,-10000,0,2,-10000,-10000,2,-300000000,-300000000,chaine,1,0,0,chaine,-200000,-200000,0,0,0,0,1,1\n""")
        expected_df_GPA_List_str = str(
            "<GPA_List>\n#GPA_No,Chip_X,Chip_Y,GP_ID\n1,2,4,1\n2,6,4,1\n3,3,7,1\n")
        expected_df_GP_Offset_str = str(
            "<GP_Offset>\n#Offset_X,Offset_Y\n0,0\n")
        expected_df_EPA_List_str = str(
            "<EPA_List>\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode\n1,1,1,1,1")

        assert hss_str == expected_df_first_level_str + expected_df_C_S_str + expected_df_GP_C_S_str + expected_df_Unit_str + \
            expected_df_GP_Data_str + expected_df_EPS_Data_str + \
            expected_df_GPA_List_str + expected_df_GP_Offset_str + expected_df_EPA_List_str

    def test_rename_eps_data_header(self):
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)
        # passes with \n
        string_to_edit = "Type1,Type12,Type100\n1,2,3\n1,2,3\n"

        # Act
        new_string = hss_creator.rename_eps_data_header(string_to_edit)

        # Assert
        expected_new_string = "Type,Type,Type\n1,2,3\n1,2,3\n"
        assert new_string == expected_new_string

    def test_set_commas_afterwards(self):
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        hss_creator = HssCreator(pd.DataFrame(), template=test_json_template)
        hss_creator.json_to_dataframe()
        string_to_modify_1 = "<GP_Data>\n" + \
            hss_creator.dict_of_second_level_df["<GP_Data>"].to_csv(
                index=False)
        # string_to_modify_2 =

        # Act
        # test1
        modified_string_1 = hss_creator.set_commas_afterwards(
            string_to_modify_1)
        # test2
        # whole_test_recipe = hss_creator.dataframe_to_hss()
        # string_to_modify_2 = hss_creator.rename_eps_data_header(whole_test_recipe)
        # modified_string_2 = hss_creator.set_commas_afterwards(string_to_modify_2)

        # Assert
        expected_modified_string_1 = "<GP_Data>,,,,,,\nGP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT\n1,1,20,20,,210,90\n,,,,,,\n"
        # expected_modified_string_2 = "<FileID>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\nLIDP00,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Version>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n6,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Revision>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<CoordinateSystem>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Type,ACD_Type,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GPCoordinateSystem>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Type,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Unit>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Coordinate,MP_Box,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GP_Data>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,20,20,chef_OM_default,210,90,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<EPS_Data>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#EPS_ID,Type,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_Scan_X,EP_Mag_Scan_Y,EP_Rot,Type,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type,EP_ABCC_X,EP_ABCC_Y,Type,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_Cursor_Size_X,MP1_SA_Out,MP1_Cursor_Size_Y,MP1_MeaLeng,MP1_Direction\n1,1,-300000000,-300000000,1,'chaine',1,'chaine','chaine','chaine','chaine',2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,1000,1000,[0.0, 0.0],2,-10000,-10000,0,2,-10000,-10000,0,2,-10000,-10000,2,-300000000,-300000000,'chaine',1,0,0,'chaine',-200000,-200000,0,0,0,0,1,1\n<GPA_List>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#GPA_No,Chip_X,Chip_Y,GP_ID,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,2,4,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n2,6,4,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n3,3,7,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GP_Offset>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Offset_X,Offset_Y,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<EPA_List>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,1,1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"
        assert modified_string_1 == expected_modified_string_1
        # assert modified_string_2 == expected_modified_string_2
        # assert hss_creator.num_columns == 3  # ?

    def test_write_in_file(self):
        '''checks for file writing and content written'''
        # Arrange
        test_json_template = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_template.json"
        test_tmp_path = "/work/opc/all/users/chanelir/semrc/tests/test_hss_modules/test_temp_output.hss"
        hss_creator = HssCreator(
            pd.DataFrame(), template=test_json_template, output_file=test_tmp_path)

        # Act
        hss_creator.write_in_file(0)

        # Assert
        with open(test_tmp_path, 'r') as f:
            hss_str = f.read()
        # FIXME beware str "" @ [0.0, 0.0]
        expected_hss_str = """<FileID>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\nLIDP00,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Version>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n6,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Revision>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<CoordinateSystem>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Type,ACD_Type,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GPCoordinateSystem>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Type,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<Unit>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Coordinate,MP_Box,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GP_Data>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#GP_ID,Type,GP_X,GP_Y,GP_Template,GP_MAG,GP_ROT,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,20,20,chef_OM_default,210,90,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<EPS_Data>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#EPS_ID,Type,Move_X,Move_Y,Mode,EPS_Name,Ref_EPS_ID,EPS_Template,AP1_Template,AP2_Template,EP_Template,Type,AP1_X,AP1_Y,AP1_Mag,AP1_Rot,Type,AP1_AF_X,AP1_AF_Y,AP1_AF_Mag,Type,AP1_AST_X,AP1_AST_Y,AP1_AST_Mag,Type,AP2_X,AP2_Y,AP2_Mag,AP2_Rot,Type,AP2_AF_X,AP2_AF_Y,AP2_AF_Mag,Type,AP2_AST_X,AP2_AST_Y,AP2_AST_Mag,EP_Mag_Scan_X,EP_Mag_Scan_Y,EP_Rot,Type,EP_AF_X,EP_AF_Y,EP_AF_Mag,Type,EP_AST_X,EP_AST_Y,EP_AST_Mag,Type,EP_ABCC_X,EP_ABCC_Y,Type,MP1_X,MP1_Y,MP1_Template,MP1_PNo,MP1_DNo1,MP1_DNo2,MP1_Name,MP1_TargetCD,MP1_PosOffset,MP1_SA_In,MP1_Cursor_Size_X,MP1_SA_Out,MP1_Cursor_Size_Y,MP1_MeaLeng,MP1_Direction,\n1,1,-300000000,-300000000,1,chaine,1,chaine,chaine,chaine,chaine,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,1000,0,2,-300000000,-300000000,0,2,-300000000,-300000000,0,1000,1000,"[0.0, 0.0]",2,-10000,-10000,0,2,-10000,-10000,0,2,-10000,-10000,2,-300000000,-300000000,chaine,1,0,0,chaine,-200000,-200000,0,0,0,0,1,1\n<GPA_List>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#GPA_No,Chip_X,Chip_Y,GP_ID,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,2,4,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n2,6,4,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n3,3,7,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<GP_Offset>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#Offset_X,Offset_Y,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n0,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n<EPA_List>,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n#EPA_No,Chip_X,Chip_Y,EPS_ID,Move_Mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n1,1,1,1,1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n"""

        assert hss_str == expected_hss_str
