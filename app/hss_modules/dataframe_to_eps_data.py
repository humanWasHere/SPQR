import pandas as pd
import numpy as np


# TODO if info is from genepy, get genepy mapping / genepy type of recipe
# TODO recloisonner le code pour simplifier les sorties de test -> <EPS_Data> section trop longue pour test
class DataFrameToEPSData:
    '''this class manages the creation of the <EPS_Data> section only'''
    FIXED_VALUES = {
        'Type1': 1,
        'Type2': 2,
        'Type3': 2,
        'AP1_Mag': 45000,
        'AP1_AF_Mag': 45000,
        'AP1_Rot': 0,
        'MP1_X': 0,
        'MP1_Y': 0
    }

    # mapping should not be used to assign data ! just make a link between 2 dfs
    MAPPING = {
        'EPS_Name': "name",
        'Move_X': "x",
        'Move_Y': "y",
        "MP_TargetCD": "target_cd"
    }

    def __init__(self, core_data: pd.DataFrame, step: str = "PH"):
        # TODO:  validate data (columns, type, nan...)
        self.core_data = core_data  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame()
        assert step in {"PH", "ET"}
        self.step = step

    def mapping_from_df(self) -> None:
        '''makes a link between gauge df and actual column name of recipe header'''
        for csv_col, gauge_col in self.MAPPING.items():
            self.eps_data[csv_col] = self.core_data[gauge_col]

    def mapping_from_fix_values(self):
        for csv_col, value in self.FIXED_VALUES.items():
            self.eps_data[csv_col] = value

    # method naming based on Hitachi doc
    def set_eps_data_id(self):
        # __________EPS_ID section__________
        self.eps_data['EPS_ID'] = range(1, min(self.core_data.shape[0] + 1, 9999))
        if any(id > 9999 for id in self.eps_data['EPS_ID']):
            raise ValueError("EPS_ID values cannot exceed 9999")

    def set_eps_data_move_modification(self):
        # Type1, Move_X and Move_Y are mapped
        # __________Mode section__________
        # should be 1 normal or 2 differential
        # FIXME input logic since value is hard coded
        mode = 1
        self.eps_data["Mode"] = np.where(mode == 1, 1, 2)

    def set_eps_data_eps_modification(self):
        # from eps_name to fer_eps_id
        # EPS_Name is mapped
        # Ref_EPS_ID has default template value
        pass

    def set_eps_data_template(self):
        # from eps_template to ep_template
        # __________EPS_Template section__________
        # FIXME is it fix ? 'EPS_Template': "EPS_Default"
        self.eps_data['EPS_Template'] = dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step]
        pass

    def set_eps_data_ap1_modification(self):
        # from type to AP1_AST_Mag
        pass

    def set_eps_data_ap2_modification(self):
        # from type to AP2_AST_Mag
        # AP1_Mag, AP1_Rot, AP1_AF_Mag are mapped
        pass

    def set_eps_data_ep_modification(self):
        # from EP_Mag_X to EP_ABCC_X
        # FIXME should be after MP_Direction ?
        # __________EP_Rot section__________
        # TODO est ce que c'est à calculer en fonction de plusieurs MP ?
        # pb for tests ? .get() instead of [], method to handle cases where a key is missing
        self.eps_data["EP_Rot"] = np.where(self.core_data.orient == "x", 0, 90)  # self.core_data.orient is equal to MP1_Direction value
        pass

    def set_eps_data_mp1(self):
        # from EP_Mag_X to EP_ABCC_X
        # MP1_X/Y are mapped
        # __________MP1_SA_In section__________
        #     search_area = self.eps_data.MP1_TargetCD * \
        #         self.eps_data.EP_Mag_X * 512 / 1000 / 135000 / 3
        #     # cursor_size = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
        #     # Limit search area to 30 pixels / todo: handle NaN
        #     self.eps_data['MP1_SA_In'] = self.eps_data['MP1_SA_Out'] = search_area.fillna(
        #         500).astype(int).clip(upper=30)

        # __________MP1_MeaLeng section__________
        #     self.eps_data['MP1_MeaLeng'] = self.measleng  # TODO: compute
        # __________MP1_PNo section__________
        self.eps_data['MP1_PNo'] = self.eps_data['EPS_ID']  # TODO: move to MP
        # __________MP_Direction__________
        self.eps_data["MP1_Direction"] = self.core_data.orient

    def get_eps_data(self) -> pd.DataFrame:
        '''callable method (destination HssCreator) which returns the EPS_Data dataframe containing the values'''
        # do not change order
        self.mapping_from_df()
        self.mapping_from_fix_values()
        self.set_eps_data_id()
        self.set_eps_data_move_modification()
        self.set_eps_data_eps_modification()
        self.set_eps_data_template()
        self.set_eps_data_ap1_modification()
        self.set_eps_data_ap2_modification()
        self.set_eps_data_ep_modification()
        self.set_eps_data_mp1()
        return self.eps_data
