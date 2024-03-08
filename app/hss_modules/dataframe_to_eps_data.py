import pandas as pd
import numpy as np

# FIXME changer l'éclatement du code en suivant les méthodes en commentaire


# TODO if info is from genepy, get genepy mapping / genepy type of recipe
# TODO recloisonner le code pour simplifier les sorties de test -> <EPS_Data> section trop longue pour test
class DataFrameToEPSData:
    '''this class manages the creation of the <EPS_Data section> only'''
    DEFAULTS = {
        'Mode': 1,
        'EPS_Template': "EPS_Default",
        'AP2_Template': "OPC_AP2_Off",
        'AP1_Mag': 45000,
        'AP1_AF_Mag': 45000,
        'AP1_Rot': 0,
        'MP1_X': 0,
        'MP1_Y': 0
    }

    # mapping should not be used to assign data ! just make a link between 2 dfs
    MAPPING_Genepy = {
        'EPS_Name': "Gauge name",
        'Move_X': "X_coord_Pat",
        'Move_Y': "Y_coord_Pat",
        "MP_TargetCD": " min_dimension(nm)"
    }

    def __init__(self, gauges: pd.DataFrame, step: str = "PH"):
        # TODO:  validate data (columns, type, nan...)
        self.gauges = gauges  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame()
        assert step in {"PH", "ET"}
        self.step = step
        # following __init__ lines should not be called like that (testing and separation purpose)
        # self.eps_data_mapping()
        # self.global_eps_data_filling()

    def eps_data_mapping(self) -> None:
        '''makes a link between gauge df and actual column name of recipe header'''
        # TODO placer ici (?) une logique sélectionnant le type de recette. Ici, depuis un ssfile genepy
        # applying mapping and so merged_df values to eps_data_df
        for csv_col, gauge_col in self.MAPPING_Genepy.items():
            self.eps_data[csv_col] = self.gauges[gauge_col]

    # # method naming based on Hitachi doc
    # def set_eps_data_id():
    #     # first eps line
    #     pass

    # def set_eps_data_move_modification():
    #     # from type to mode
    #     pass

    # def set_eps_data_eps_modification():
    #     # from eps_name to fer_eps_id
    #     pass

    # def set_eps_data_template():
    #     # from eps_template to ep_template
    #     pass

    # def set_eps_data_ap1_modification():
    #     # from type to AP1_AST_Mag
    #     pass

    # def set_eps_data_ap2_modification():
    #     # from type to AP2_AST_Mag
    #     pass

    # def set_eps_data_ep_modification():
    #     # from EP_Mag_X to EP_ABCC_X
    #     pass

    # def set_eps_data_mp1():
    #     # from EP_Mag_X to EP_ABCC_X
    #     pass

    def global_eps_data_filling(self) -> None:
        '''Generate unique IDs and fill columns with default values'''
        # __________EPS_ID section__________
        self.eps_data['EPS_ID'] = range(1, min(self.gauges.shape[0] + 1, 9999))
        # preventing data to be out of range -> match doc
        if any(id > 9999 for id in self.eps_data['EPS_ID']):
            raise ValueError("EPS_ID values cannot exceed 9999")

        # __________EP_Template section__________
        # FIXME is it correct setting ?
        self.eps_data['EP_Template'] = dict(
            PH="banger_EP_F16", ET="banger_EP_F32")[self.step]

        # __________MP_Direction__________
        # FIXME it is hard coded
        # written since it is mandatory for EP_Rot
        self.eps_data["MP1_Direction"] = 1

        # __________EP_Rot section__________
        # TODO est ce que c'est à calculer en fonction de plusieurs MP ?
        # FIXME est ce que la ligne est validée par Romain ?
        # ligne suivante bien pour du test ?
        # .get() instead of [], method to handle cases where a key is missing
        x = 1
        self.eps_data["EP_Rot"] = np.where(self.eps_data["MP1_Direction"] == x, 0, 90)

        # __________Mode section__________
        # should be 1 normal or 2 differential
        # FIXME input logic since value is hard coded
        mode = 1
        self.eps_data["Mode"] = np.where(mode == 1, 1, 2)

        # __________MP1_PNo section__________
        # input logic

        # __________MP1_SA_In section__________
    #     search_area = self.eps_data.MP1_TargetCD * \
    #         self.eps_data.EP_Mag_X * 512 / 1000 / 135000 / 3
    #     # cursor_size = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
    #     # Limit search area to 30 pixels / todo: handle NaN
    #     self.eps_data['MP1_SA_In'] = self.eps_data['MP1_SA_Out'] = search_area.fillna(
    #         500).astype(int).clip(upper=30)

        # __________MP1_MeaLeng section__________
    #     self.eps_data['MP1_MeaLeng'] = self.measleng  # TODO: compute

    def get_eps_data(self) -> pd.DataFrame:
        '''callable method (destination HssCreator) which returns the EPS_Data dataframe containing the values'''
        self.eps_data_mapping()
        self.global_eps_data_filling()
        # # new sections
        # self.set_eps_data_id()
        # self.set_eps_data_move_modification()
        # self.set_eps_data_eps_modification()
        # self.set_eps_data_template()
        # self.set_eps_data_ap1_modification()
        # self.set_eps_data_ap2_modification()
        # self.set_eps_data_ep_modification()
        # self.set_eps_data_mp1()
        return self.eps_data
