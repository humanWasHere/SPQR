import pandas as pd
import numpy as np

# FIXME changed orientation in core_data
# WARNING dependance et ordre de définition
# TODO if info is from genepy, get genepy mapping / genepy type of recipe
# TODO recloisonner le code pour simplifier les sorties de test -> <EPS_Data> section trop longue pour test


class DataFrameToEPSData:
    '''this class manages the creation of the <EPS_Data> section only'''
    FIXED_VALUES = {
        'Mode': 1,
        'EPS_Template': "EPS_Default",
        'AP2_Template': "OPC_AP2_Off",
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
    genepy_mapping = {
        'EPS_Name': "name",
        'Move_X': "x",
        'Move_Y': "y",
        'EP_Mag_X': "magnification",
        # 'EP_AF_X': "x_af",
        # 'EP_AF_Y': "y_af",
        'EP_AF_Mag': "magnification",
        'AP1_X': "x_ap",
        'AP1_Y': "y_ap",
        'AP1_AF_X': "x_ap",
        'AP1_AF_Y': "y_ap"
    }

    calibre_ruler_mapping = {
        'EPS_Name': "name",
        'Move_X': "x",
        'Move_Y': "y",
        'EP_Mag_X': "magnification",
        # 'EP_AF_X': "x_af",
        # 'EP_AF_Y': "y_af",
        'EP_AF_Mag': "magnification"
    }

    def __init__(self, core_data: pd.DataFrame, step: str = "PH"):
        # TODO:  validate data (columns, type, nan...)
        self.core_data = core_data  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame()
        assert step in {"PH", "ET"}
        self.step = step

    def add_mp_width(self, mp_no=1, direction: str = None, measleng: int = 100):
        """Add a width measurement point (line/space depending on MP template) at image center"""
        self.eps_data[[f"MP{mp_no}_X", f"MP{mp_no}_Y"]] = (0, 0)  # image center
        if direction is None:
            # same as commented in measure -> lines 112 to 115
            target_cd = self.core_data[['x_dim', 'y_dim']].min(axis=1)
            self.core_data["orientation"] = np.where(target_cd == self.core_data.y_dim, "Y", "X")
            self.eps_data[f'MP{mp_no}_TargetCD'] = target_cd
            self.eps_data[f'MP{mp_no}_Direction'] = self.core_data.orientation
            self.eps_data[f'MP{mp_no}_Name'] = self.core_data.name
        else:
            assert direction.upper() in {'X', 'Y'}
            self.eps_data[f'MP{mp_no}_TargetCD'] = self.core_data[f'cd_{direction.lower()}']
            self.eps_data[f'MP{mp_no}_Direction'] = direction
            self.eps_data[f'MP{mp_no}_Name'] = self.core_data.name + "_" + self.eps_data[f'MP{mp_no}_Direction']

        # Compute MP width/length (from SEM procedure)
        target_cd_pixel = self.eps_data[f'MP{mp_no}_TargetCD'] * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
        # Limit search area to 30 pixels  #TODO: handle NaN & pitch (SA_out) # TODO check box overlap vs targetCD (SA_in)
        self.eps_data[f'MP{mp_no}_SA_In'] = self.eps_data[f'MP{mp_no}_SA_Out'] = (target_cd_pixel / 3).fillna(500).astype(int).clip(upper=30)
        self.eps_data[f'MP{mp_no}_MeaLeng'] = measleng or self.measleng  # TODO: compute vs height
        self.eps_data['MP1_PNo'] = self.eps_data['EPS_ID']

    def distribute_mapping(self, parser_input) -> None:
        '''makes a link between gauge df and actual column name of recipe header for genepy ssfile parser input'''
        mapping = None
        if parser_input == 'genepy_ssfile':
            mapping = self.genepy_mapping
        elif parser_input == 'calibre_ruler':
            mapping = self.calibre_ruler_mapping  # This line was missing the assignment to 'mapping'
        else:
            raise ValueError("parser input should be 'genepy_ssfile' or 'calibre_ruler'")
        for csv_col, gauge_col in mapping.items():  # Use the 'mapping' variable here
            self.eps_data[csv_col] = self.core_data[gauge_col] 

    # def mapping_from_df(self) -> None:
    #     '''makes a link between gauge df and actual column name of recipe header'''
    #     for csv_col, gauge_col in self.MAPPING.items():
    #         self.eps_data[csv_col] = self.core_data[gauge_col]

    def mapping_from_fix_values(self):
        for csv_col, value in self.FIXED_VALUES.items():
            self.eps_data[csv_col] = value

    # method naming based on Hitachi doc
    def set_eps_data_id(self):
        # __________EPS_ID section__________
        self.eps_data['EPS_ID'] = range(1, min(self.core_data.shape[0] + 1, 9999))
        if any(id > 9999 for id in self.eps_data['EPS_ID']):
            raise ValueError("EPS_ID values cannot exceed 9999")

    def set_eps_data_eps_modification(self):
        # from eps_name to fer_eps_id
        # EPS_Name is mapped
        # Ref_EPS_ID has default template value
        pass

    def set_eps_data_template(self):
        # from eps_template to ep_template
        # __________EPS_Template section__________
        self.eps_data['EP_Template'] = dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step]

    def set_eps_data_ap1_modification(self):
        # from type to AP1_AST_Mag
        pass

    def set_eps_data_ap2_modification(self):
        # from type to AP2_AST_Mag
        # AP1_Mag, AP1_Rot, AP1_AF_Mag are mapped
        pass

    def set_eps_data_ep_modification(self):
        """Columns from EP_Mag_X to EP_ABCC_X"""
        # __________EP_Rot section__________
        # TODO auto-rotation en fonction de plusieurs MP ? # FIXME demander a Julien + Mode
        self.eps_data["EP_Rot"] = np.where(self.core_data.orientation == "x", 0, 90)  # self.core_data.orient is equal to MP1_Direction value
        # EP_AF_X, EP_AF_Y
        pass

    def get_eps_data(self, parser_input) -> pd.DataFrame:
        '''callable method (destination HssCreator) which returns the EPS_Data dataframe containing the values'''
        print('3. <EPS_Data> section creation')  # to log
        self.distribute_mapping(parser_input)
        self.mapping_from_fix_values()
        self.set_eps_data_id()
        self.add_mp_width(1)
        self.set_eps_data_eps_modification()
        self.set_eps_data_template()
        self.set_eps_data_ap1_modification()
        self.set_eps_data_ap2_modification()
        self.set_eps_data_ep_modification()
        if not self.eps_data.empty:  # better check + log
            print('\t<EPS_Data> created')
        return self.eps_data
