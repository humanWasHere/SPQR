import pandas as pd
from pathlib import Path


class SectionMaker:
    '''this class is used to create, fill or modify the values of all second level sections except <EPS_Data> section. If not modified, value is set default as in template.json'''

    def __init__(self, df_dict):
        self.coordinate_system = df_dict["<CoordinateSystem>"]
        self.gp_coordinate_system = df_dict["<GPCoordinateSystem>"]
        self.unit = df_dict["<Unit>"]
        self.gp_data = df_dict["<GP_Data>"]
        self.gpa_list = df_dict["<GPA_List>"]
        self.gp_offset = df_dict["<GP_Offset>"]
        self.epa_list = df_dict["<EPA_List>"]
        self.idd_cond = df_dict["<IDD_Cond>"]
        self.idd_layer_data = df_dict["<IDD_Layer_Data>"]
        self.image_env = df_dict["<ImageEnv>"]

    # by default, if there is no modification, each section returns the default value in assets/template_SEM_recipe.json
    def make_coordinate_system_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to coordinate system section by calculation or definition'''
        return self.coordinate_system

    def make_gp_coordinate_system_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to gp coordinate system section by calculation or definition'''
        return self.gp_coordinate_system

    def make_unit_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to unit section by calculation or definition'''
        return self.unit

    def make_gp_data_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to gp data section by calculation or definition'''
        # __________GP_ID section__________
        # self.gp_data['GP_ID'] = range(1, min(self.corresponding_data.shape[0] + 1, 10))
        # # preventing data to be out of range -> match doc
        # if any(id > 10 for id in self.gp_data['GP_ID']):
        #     raise ValueError("GP_ID values cannot exceed 10")
        # __________Type section__________
        # should be one
        # TODO test if type here is always one -> test template
        # __________GP_X section__________
        # __________GP_Y section__________
        # __________GP_Template section__________
        # FIXME change filling to line filling. not column filling
        if self.gp_data["GP_Template"].isna().any():
            raise ValueError("GP_Template is mandatory")

        # __________GP_MAG section__________
        if self.gp_data["GP_Template"].str.contains("OM").any():  # TODO: check in template file
            # value should be 104 or 210
            self.gp_data["GP_MAG"] = 210
            if not self.gp_data["GP_MAG"].isin([104, 210]).all():
                raise ValueError("GP_MAG for OM should be either 104 or 210")
        elif self.gp_data["GP_Template"].str.contains("SEM").any():
            # TODO comment savoir quelle valeur entre 1000 et 500000 ?
            self.gp_data["GP_MAG"] = 500000
            if not self.gp_data["GP_MAG"].between(1000, 500_000).any():
                raise ValueError(
                    "GP_MAG for SEM should be between 1000 and 500000")

        # __________GP_ROT section__________
        return self.gp_data

    def make_gpa_list_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to gpa list section by calculation or definition'''
        return self.gpa_list

    def make_gp_offset_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to gp offset section by calculation or definition'''
        return self.gp_offset

    def make_epa_list_section(self) -> pd.DataFrame:
        '''this meathod set corresponding values to epa list section by calculation or definition'''
        return self.epa_list

    def make_idd_cond_section(self, layout, topcell) -> pd.DataFrame:
        self.idd_cond.loc[0, ["DesignData", "CellName"]] = Path(layout).stem, topcell
        return self.idd_cond

    def make_idd_layer_data_section(self, mask_layer) -> pd.DataFrame:
        self.idd_layer_data.loc[0, ["LayerNo", "DataType"]] = 0, 114  # TODO link with step / target layer
        self.idd_layer_data.loc[1:, "LayerNo"] = mask_layer  # TODO troncate of round ?
        return self.idd_layer_data

    def make_image_env_section(self) -> pd.DataFrame:
        return self.image_env
