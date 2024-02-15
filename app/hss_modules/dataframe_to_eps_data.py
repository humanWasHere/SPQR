import pandas as pd


class DataFrameToEPSData:
    # DEFAULTS = {
    #     'Mode': 1,
    #     'EPS_Template': "EPS_Default",
    #     'AP2_Template': "OPC_AP2_Off",
    #     'AP1_Mag': 45000,
    #     'AP1_AF_Mag': 45000,
    #     'AP1_Rot': 0,
    #     'MP1_X': 0,
    #     'MP1_Y': 0
    # }
    # MAP = {
    #     'Move_X': "x",
    #     'Move_Y': "y",
    #     'EPS_Name': "name",
    #     'AP1_X': "x_ap_rel",
    #     'AP1_Y': "y_ap_rel",
    #     'AP1_AF_X': "x_ap_rel",
    #     'AP1_AF_Y': "y_ap_rel",
    #     'EP_Mag_X': "mag",
    #     'EP_AF_X': "x_af_rel",
    #     'EP_AF_Y': "y_af_rel",
    #     'EP_AF_Mag': "mag",
    #     'MP1_Name': "name",
    #     'MP1_TargetCD': "target_cd",
    #     'MP1_Direction': "orient"
    # }
    MAPPING_Genepy = {
        'EPS_Name': "Gauge name",
        'Move_X': "X_coord_Pat",
        'Move_Y': "Y_coord_Pat",
        "MP_TargetCD": " min_dimension(nm)"
    }
    # correspondance entre min template (à ne pas toucher) et valeurs réalistes
    # inspired from banger-283UA-ZACT-PH-SRAM-FEM hss
    test_MAPPING_EPS_Data_from_template = {
        "Mode": 1,
        "AP1_X": -1000,
        "AP1_Y": 0,
        'AP1_Mag': 45000,
        'AP1_AF_Mag': 45000,
        'AP1_Rot': 0,
        "AP1_AF_X": -300000000,
        "AP1_AF_Y": -300000000,
        "AP1_AST_X": -300000000,
        "AP1_AST_Y": -300000000,
        "AP1_AST_Mag": 0,
        "AP2_X": -300000000,
        "AP2_Y": -300000000,
        "AP2_Mag": 1000,
        "AP2_Rot": 90,
        "AP2_AF_X": -300000000,
        "AP2_AF_Y": -300000000,
        "AP2_AF_Mag": 0,
        "AP2_AST_X": -300000000,
        "AP2_AST_Y": -300000000,
        "AP2_AST_Mag": 0,
        "EP_Mag_Scan_X": 1000,
        "EP_Mag_Scan_Y": 1000,
        "EP_Rot": "0,0",
        "EP_AF_X": -10000,
        "EP_AF_Y": -10000,
        "EP_AF_Mag": 0,
        "EP_AST_X": -10000,
        "EP_AST_Y": -10000,
        "EP_AST_Mag": 0,
        "EP_ABCC_X": -10000,
        "EP_ABCC_Y": -10000,
        "MP_X": -300000000,
        "MP_Y": -300000000,
        "MP_Template": "chaine",
        "MP_PNo": 1,
        "MP_DNo1": 0,
        "MP_DNo2": 0,
        "MP_Name": "chaine",
        "MP_TargetCD": -200000,
        "MP_PosOffset": -200000,
        "MP_SA_In": 0,
        "MP_Cursor_Size_X": 0,
        "MP_SA_Out": 0,
        "MP_Cursor_Size_Y": 0,
        "MP_MeaLeng": 1,
        "MP_Direction": 1
    }

    def __init__(self, gauges: pd.DataFrame, step: str = "PH"):
        # TODO:  validate data (columns, dtype, nan...)
        self.gauges = gauges  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame()
        assert step in {"PH", "ET"}
        self.step = step

        self.global_eps_data_filling()
        # self.map_columns()
        # self.autofill_columns()

    # def set_rotation(self):
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90

    #     rot = np.where(self.eps_data['MP1_Direction'] == "X", 0, 90)
    #     # elif Y
    #     return rot

    # def test(self):
    #     TEST_MAPPING = {
    #         'Mode': 1,
    #         'EPS_Template': "EPS_Default",
    #         'AP2_Template': "OPC_AP2_Off",
    #         'AP1_Mag': 45000,
    #         'AP1_AF_Mag': 45000,
    #         'AP1_Rot': 0,
    #         'MP1_X': 0,
    #         'MP1_Y': 0,
    #         'Move_X': self.gauges["x"],
    #         'Move_Y': self.gauges["y"],
    #         'EP_Template': dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step],
    #         'EP_Rot': self.set_rotation()
    #     }

    def global_eps_data_filling(self):
        """Generate unique IDs and fill columns with default values"""
        # TODO placer ici (?) une logique sélectionnant le type de recette. Ici, depuis un ssfile genepy
        # applying mapping and so merged_df values to eps_data_df
        for csv_col, value in self.MAPPING_Genepy.items():
            self.eps_data[csv_col] = self.gauges[value]

        # # applying test mapping to eps_data_df
        # for csv_col, value in self.test_MAPPING_EPS_Data_from_template.items():
        #     self.eps_data[csv_col] = value

        # __________EPS_ID section__________
        self.eps_data['EPS_ID'] = range(1, min(self.gauges.shape[0] + 1, 9999))
        # preventing data to be out of range -> match doc
        if any(id > 9999 for id in self.eps_data['EPS_ID']):
            raise ValueError("EPS_ID values cannot exceed 9999")

        # __________Mode section__________
        # should be 1 normal or 2 differential

        # __________GP_Template section__________
        # must match type of measure -> OM / SEM
        # FIXME must work
        # if self.eps_data['GP_Template'] == "":
        #     # if type_of_measure is "optical":
        #     self.eps_data['GP_Template'] = "chef_OM_default"  # is xml in rcpd machine ?

        # TODO if GP_Template == "chef_OM_default":
        # GP_MAG = 210

        # self.eps_data['MP1_PNo'] = self.eps_data['#EPS_ID']
        # for csv_col, value in self.DEFAULTS.items():
        #     self.eps_data[csv_col] = value

    # def map_columns(self):
    #     """Map gauge dataframe columns with corresponding recipe columns without further processing"""
    #     for csv_col, gauge_col in self.MAP.items():
    #         self.eps_data[csv_col] = self.gauges[gauge_col]

    # # TODO intégrer l'autofill à la création du df eps_data
    # def autofill_columns(self):
    #     """Fill more columns using logic"""
    #     self.eps_data['EP_Template'] = dict(
    #         PH="banger_EP_F16", ET="banger_EP_F32")[self.step]

    #     # Set rotation
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90
    #     # Compute measure point width/length (from SEM procedure)
    #     # TODO: MP_Cursor_Size_X/Y etc. for Ellipse. cf doc HSS p. 67
    #     search_area = self.eps_data.MP1_TargetCD * \
    #         self.eps_data.EP_Mag_X * 512 / 1000 / 135000 / 3
    #     # cursor_size = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
    #     # Limit search area to 30 pixels / todo: handle NaN
    #     self.eps_data['MP1_SA_In'] = self.eps_data['MP1_SA_Out'] = search_area.fillna(
    #         500).astype(int).clip(upper=30)
    #     self.eps_data['MP1_MeaLeng'] = self.measleng  # TODO: compute
    #     # Fill Type columns. First one is 1, all others are 2 (?)
    #     # list of column indices  #TODO 65 for 1 MP, 66 for 2 MP...
    #     # type_cols = [i for i, label in enumerate(
    #     #     EPS_COLUMNS[:65]) if label == "Type"]
    #     # self.eps_data.iloc[:, type_cols] = 2
    #     self.eps_data.iloc[:, 1] = 1

    # type must be at the end of the flow

    def get_eps_data(self) -> pd.DataFrame:
        '''callable method (destination HssCreator) which returns the EPS_Data dataframe containing the values'''
        # print(self.eps_data.head().to_string())
        return self.eps_data
