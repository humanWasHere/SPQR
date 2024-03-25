import pandas as pd


class SectionMaker:
    '''this class is used to create, fill or modify the values of all second level sections except <EPS_Data> section. If not modified, value is set default as in template.json'''

    def __init__(self, dictionnary):
        self.df_dict = dictionnary
        self.coordinate_system = self.df_dict["<CoordinateSystem>"]
        self.gp_coordinate_system = self.df_dict["<GPCoordinateSystem>"]
        self.unit = self.df_dict["<Unit>"]
        self.gp_data = self.df_dict["<GP_Data>"]
        self.gpa_list = self.df_dict["<GPA_List>"]
        self.gp_offset = self.df_dict["<GP_Offset>"]
        self.epa_list = self.df_dict["<EPA_List>"]

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
