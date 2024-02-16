# import pandas as pd


class sectionMaker:
    def __init__(self, dictionnary):
        self.df_dict = dictionnary
        self.coordinate_system = self.df_dict["<CoordinateSystem>"]
        self.gp_coordinate_system = self.df_dict["<GPCoordinateSystem>"]
        self.unit = self.df_dict["<Unit>"]
        self.gp_data = self.df_dict["<GP_Data>"]
        self.gpa_list = self.df_dict["<GPA_List>"]
        self.gp_offset = self.df_dict["<GP_Offset>"]
        self.epa_list = self.df_dict["<EPA_List>"]

    def make_coordinate_system_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        return self.coordinate_system

    def make_gp_coordinate_system_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        return self.gp_coordinate_system

    def make_unit_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        return self.unit

    def make_gp_data_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        # TODO implement the right logic -> get the correct info
        # __________GP_Template section__________
        self.gp_data["GP_Template"] = "chef_OM_default"
        # # __________Mode section__________
        # if self.gp_data["GP_Template"] == "chef_OM_default":
        #     # attribute default value
        #     gp_mag_OM_default = 210
        #     if self.gp_data["GP_MAG"] >= 104 and self.gp_data["GP_MAG"] <= 210:
        #         self.gp_data["GP_MAG"] = gp_mag_OM_default
        #     else:
        #         raise ValueError("Value for OM should be between 104 and 210 - change GP_Template or this value")
        # # Même chose pour les SEM
        # # elif self.gp_data["GP_Template"] == "chef_SEM_default":
        #     # gp_mag_SEM_default = 500000
        #     # if self.gp_data["GP_MAG"] >= 1000 and self.gp_data["GP_MAG"] <= 500000:
        # print(pd.Series(self.gp_data).to_string())
        return self.gp_data

    def make_gpa_list_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        return self.gpa_list

    def make_gp_offset_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        return self.gp_offset

    def make_epa_list_section(self):
        '''this meathod set corresponding values to contest by calculation or definition'''
        return self.epa_list
