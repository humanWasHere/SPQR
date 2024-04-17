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
    def dict_dataframe_section_maker(self):
        # TODO TEMP !!! since template_to_all_sections.py needs to be implemented
        default_df = pd.DataFrame({
            "col1": [1, 1, 1],
            "col2": [2, 2, 2],
            "col3": [3, 3, 3]
        })
        dict_df = {
            "<CoordinateSystem>": default_df,
            "<GPCoordinateSystem>": default_df,
            "<Unit>": default_df,
            "<GPA_List>": default_df,
            "<GP_Offset>": default_df,
            "<EPA_List>": default_df
        }
        return dict_df

    # FIXME not correct anymore ???
    @pytest.fixture
    def section_maker_instance_om(self):
        return SectionMaker(self.dict_dataframe_section_maker, "OM")

    @pytest.fixture
    def section_maker_instance_sem(self):
        return SectionMaker(self.dict_dataframe_section_maker, "SEM")

    @pytest.fixture
    def dict_with_gp_data(self):
        gp_data_df_OM = pd.DataFrame({
            "GP_Template": "chef_OM_default",
            "GP_MAG": 104
        })
        gp_data_df_SEM = pd.DataFrame({
            "GP_Template": "chef_OM_default",
            "GP_MAG": 500000
        })
        if self.section_maker_instance_om == "OM":
            self.dict_dataframe_section_maker["<GP_Data>"] = gp_data_df_OM
        else:
            self.dict_dataframe_section_maker["<GP_Data>"] = gp_data_df_SEM
        return self.dict_dataframe_section_maker

    def test_make_coordinate_system_section(self):
        # TODO make it more relevant
        # Arrange
        expected_coordinate_system = pd.DataFrame({
            "col1": [1, 1, 1],
            "col2": [2, 2, 2],
            "col3": [3, 3, 3]
        })
        default_df = pd.DataFrame({
            "col1": [1, 1, 1],
            "col2": [2, 2, 2],
            "col3": [3, 3, 3]
        })
        dict_df = {
            "<CoordinateSystem>": default_df,
            "<GPCoordinateSystem>": default_df,
            "<Unit>": default_df,
            "<GPA_List>": default_df,
            "<GP_Offset>": default_df,
            "<EPA_List>": default_df
        }

        # Act
        # actual_coordinate_system = self.dict_dataframe_section_maker["<CoordinateSystem>"]
        # print(self.dict_with_gp_data["<CoordinateSystem>"])
        actual_coordinate_system = dict_df["<CoordinateSystem>"]

        # Assert
        pd.testing.assert_frame_equal(actual_coordinate_system, expected_coordinate_system)

    # def test_make_gp_coordinate_system_section(self):
    #     pass

    # def test_make_unit_section(self):
    #     pass

    # def test_make_gp_data_section(self):
    #     pass

    # def test_make_gpa_list_section(self):
    #     pass

    # def test_make_gp_offset_section(self):
    #     pass

    # def test_make_epa_list_section(self):
    #     pass
