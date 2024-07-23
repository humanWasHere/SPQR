import pandas as pd
import pytest

from app.export_hitachi.section_maker import SectionMaker


class TestSectionMaker:

    @pytest.fixture
    def section_maker(self) -> SectionMaker:
        # TODO TEMP !!! since template_to_all_sections.py needs to be implemented
        default_df = pd.DataFrame({
            "col1": [1, 1, 1],
            "col2": [2, 2, 2],
            "col3": [3, 3, 3]
        })
        gp_data_df = pd.DataFrame({
            "Type": [1, 1],
            "GP_Template": ["chef_OM_default", "chef_SEM_default"],
            "GP_Mag": [210, 500000]
        })
        idd_cond_df = pd.DataFrame({
            "DesignData": ["COMPLETED_TEMPLATE"],
            "CellName": ["OPCFIeld"]
        })
        idd_layer_data_df = pd.DataFrame({
            "LayerNo": [0, 0],
            "DataType": [114, 0],
            "Tone": [-1, -1]
        })
        recipe_df = pd.DataFrame({
            "SEMCondNo": [2]
        })
        dict_df = {
            "<CoordinateSystem>": default_df,
            "<GPCoordinateSystem>": default_df,
            "<Unit>": default_df,
            "<GP_Data>": gp_data_df,
            "<GPA_List>": default_df,
            "<GP_Offset>": default_df,
            "<EPA_List>": default_df,
            "<IDD_Cond>": idd_cond_df,
            "<IDD_Layer_Data>": idd_layer_data_df,
            "<ImageEnv>": default_df,
            "<Recipe>": recipe_df,
            "<MeasEnv_Exec>": default_df,
            "<MeasEnv_MeasRes>": default_df
        }
        return SectionMaker(dict_df)

    # @pytest.fixture
    # def dict_with_gp_data(self):
    #     gp_data_df_OM = pd.DataFrame({
    #         "GP_Template": "chef_OM_default",
    #         "GP_MAG": 104
    #     })
    #     gp_data_df_SEM = pd.DataFrame({
    #         "GP_Template": "chef_OM_default",
    #         "GP_MAG": 500000
    #     })
    #     if self.section_maker_instance_om == "OM":
    #         self.dict_dataframe_section_maker["<GP_Data>"] = gp_data_df_OM
    #     else:
    #         self.dict_dataframe_section_maker["<GP_Data>"] = gp_data_df_SEM
    #     return self.dict_dataframe_section_maker

    def test_make_gp_data_section(self, section_maker):
        # TODO
        # Arrange
        expected_df = pd.DataFrame({
            "Type": [1, 1],
            "GP_Template": ["chef_OM_default", "chef_SEM_default"],
            "GP_Mag": [210, 500000]
        })

        # Act
        section_maker.make_gp_data_section()

        # Assert
        pd.testing.assert_frame_equal(section_maker.gp_data, expected_df)

    def test_make_gp_data_section_raises_for_missing_template(self, section_maker):
        # Arrange
        section_maker.gp_data["GP_Template"] = [None, None]

        # Act / Assert
        with pytest.raises(ValueError) as excinfo:
            section_maker.make_gp_data_section()
        assert "GP_Template is mandatory" in str(excinfo.value)
        
    def test_make_idd_cond_section(self, section_maker):
        # Arrange
        test_layout_stem = "COMPLETED_TEMPLATE"
        test_layout_path = f'/path/to/{test_layout_stem}.gds'
        test_topcell = "OPCFIeld"
        expected_df = pd.DataFrame({
            "DesignData": [test_layout_stem],
            "CellName": [test_topcell]
        })

        # Act
        result_df = section_maker.make_idd_cond_section(layout=test_layout_path, topcell=test_topcell)

        # Assert
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_make_idd_layer_data_section(self, section_maker):
        # Arrange
        mask_layer = 1
        polarity = 'dark'
        expected_df = pd.DataFrame({
            "LayerNo": [0, 1],
            "DataType": [114, 0],
            "Tone": [1, 1]
        })

        # Act
        result_df = section_maker.make_idd_layer_data_section(mask_layer, polarity)

        # Assert
        pd.testing.assert_frame_equal(result_df, expected_df)

    # def test_make_image_env_section(self):
        # pass

    def test_make_recipe_section(self, section_maker):
        # Arrange
        step = "PH"
        expected_df = pd.DataFrame({
            "SEMCondNo": [2]
        })

        # Act
        result_df = section_maker.make_recipe_section(step)

        # Assert
        pd.testing.assert_frame_equal(result_df, expected_df)

    # def test_make_coordinate_system_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_epa_list_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_gp_coordinate_system_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_gp_offset_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_gpa_list_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_image_env_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_measenv_exec_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_measenv_measres_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_unit_section(self):
        # Arrange
        # Act
        # Assert