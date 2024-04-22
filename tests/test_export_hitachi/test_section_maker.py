from app.export_hitachi.section_maker import SectionMaker
# from app.hss_modules.hss_creator import HssCreator
import pytest
import pandas as pd

# FIXME nothing works :)
# TODO Beware good import in recipe type (OM or SEM)


class TestSectionMaker:

    # @pytest.fixture
    # def hss_creator_template(self):
    #     hss_creator_instance = hssCreator(pd.DataFrame())
    #     return hss_creator_instance.json_template

    @pytest.fixture
    def section_maker_instance(self):
        # TODO TEMP !!! since template_to_all_sections.py needs to be implemented
        default_df = pd.DataFrame({
            "col1": [1, 1, 1],
            "col2": [2, 2, 2],
            "col3": [3, 3, 3]
        })
        gp_data_df = pd.DataFrame({
            "GP_Template": ["chef_OM_default", "chef_SEM_default"],
            "GP_MAG": [210, 500000]
        })
        idd_cond_df = pd.DataFrame({
            "DesignData": ["COMPLETED_TEMPLATE"],
            "CellName": ["OPCFIeld"]
        })
        idd_layer_data_df = pd.DataFrame({
            "LayerNo": [0, 1],
            "DataType": [114, 114]
        })
        dict_df = {
            "<CoordinateSystem>": default_df,
            "<GPCoordinateSystem>": default_df,
            "<Unit>": default_df,
            "<GP_Data>": gp_data_df,
            "<GP_Offset>": default_df,
            "<GPA_List>": default_df,
            "<EPA_List>": default_df,
            "<IDD_Cond>": idd_cond_df,
            "<IDD_Layer_Data>": idd_layer_data_df,
            "<ImageEnv>": default_df
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

    # def test_make_coordinate_system_section(self):
        # Arrange
        # Act
        # Assert

    # def test_make_gp_coordinate_system_section(self):
    #     pass

    # def test_make_unit_section(self):
    #     pass

    # FIXME highlights default in line filling -> fills whole column
    def test_make_gp_data_section(self, section_maker_instance):
        # TODO
        # Arrange
        expected_df = pd.DataFrame({
            "GP_Template": ["chef_OM_default", "chef_SEM_default"],
            "GP_MAG": [210, 500000]
        })

        # Act
        section_maker_instance.make_gp_data_section()

        # Assert
        pd.testing.assert_frame_equal(section_maker_instance.gp_data, expected_df)

    def test_make_gp_data_section_raises_for_missing_template(self, section_maker_instance):
        # Arrange
        section_maker_instance.gp_data["GP_Template"] = [None, None]

        # Act / Assert
        with pytest.raises(ValueError) as excinfo:
            section_maker_instance.make_gp_data_section()
        assert "GP_Template is mandatory" in str(excinfo.value)

    # def test_make_gpa_list_section(self):
    #     pass

    # def test_make_gp_offset_section(self):
    #     pass

    # def test_make_epa_list_section(self):
    #     pass

    def test_make_idd_cond_section(self, section_maker_instance):
        # Arrange
        test_layout_stem = 'COMPLETED_TEMPLATE'
        test_layout_path = f'//work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/{test_layout_stem}.gds'
        test_topcell = "OPCFIeld"
        expected_df = pd.DataFrame({
            "DesignData": [test_layout_stem],
            "CellName": [test_topcell]
        })

        # Act
        result_df = section_maker_instance.make_idd_cond_section(layout=test_layout_path, topcell=test_topcell)

        # Assert
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_make_idd_layer_data_section(self, section_maker_instance):
        mask_layer_value = 1  # Valeur fictive pour l'exemple
        expected_df = pd.DataFrame({
            "LayerNo": [0, 1],
            "DataType": [114, 114]
        })

        # Act
        result_df = section_maker_instance.make_idd_layer_data_section(mask_layer_value)

        # Assert
        pd.testing.assert_frame_equal(result_df, expected_df)

    # def test_make_image_env_section(self):
        # pass
