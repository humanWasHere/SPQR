import pandas as pd
import numpy as np
from typing import Optional


class DataFrameToEPSData:
    '''this class manages the creation of the <EPS_Data> section only'''
    # mapping in which the values are values to write in the recipe (since they are fixed)
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

    # mapper which matches the values of 2 different dataframes
    MAPPING = {
        'EPS_Name': "name",
        'Move_X': "x",
        'Move_Y': "y",
        # 'EP_AF_X': "x_af",
        # 'EP_AF_Y': "y_af",
        'AP1_X': "x_ap",
        'AP1_Y': "y_ap",
        'AP1_AF_X': "x_ap",
        'AP1_AF_Y': "y_ap"
    }

    # mapper which matches the values of 2 different dataframes
    MAPPING_CORE_DATA = {
        'EP_Template': "ep_template",
        'EPS_Template': "eps_template",
        'AP1_Template': "ap1_template",
        'AP1_Mag': "ap1_mag",
        'EP_Mag_X': "magnification",
        'EP_AF_Mag': "magnification"
    }
    # FIXME to remove ?
    meas_len = 100

    def __init__(self, core_data: pd.DataFrame, user_config_info: dict = {}):
        # TODO:  validate data (columns, type, nan...) -> validator -> see when to validate in flow
        self.core_data = core_data.astype({'x': int, 'y': int, 'x_ap': int, 'y_ap': int},
                                          errors="ignore")
        self.eps_data = pd.DataFrame()
        self.json_conf = user_config_info
        self.step = self.json_conf['step']
        assert self.step in {"PH", "ET", "PH_HR", "ET_HR"}

    def add_mp_width(self, mp_no=1, direction: Optional[str] = None, measleng: int = 100) -> None:
        """Add a width measurement point (line/space depending on MP template) at image center"""
        # FIXME doesn't add more than 1 mp ?
        # TODO -> convert to nm -> MP1_X/Y ? -> at the end in hss_creator.write_in_file ?
        self.eps_data[[f"MP{mp_no}_X", f"MP{mp_no}_Y"]] = (0, 0)  # image center
        if direction is None:
            # same as commented in measure -> lines 112 to 115
            # TODO a revoir -> in core data?
            target_cd = self.core_data[['x_dim', 'y_dim']].min(axis=1)
            self.core_data["orientation"] = np.where(target_cd == self.core_data.y_dim, "Y", "X")
            self.eps_data[f'MP{mp_no}_TargetCD'] = target_cd.astype(int)
            self.eps_data[f'MP{mp_no}_Direction'] = self.core_data.orientation
            self.eps_data[f'MP{mp_no}_Name'] = self.core_data.name
        else:
            assert direction.upper() in {'X', 'Y'}
            self.eps_data[f'MP{mp_no}_TargetCD'] = self.core_data[f'cd_{direction.lower()}']
            self.eps_data[f'MP{mp_no}_Direction'] = direction
            self.eps_data[f'MP{mp_no}_Name'] = (self.core_data.name + "_" + self.eps_data[f'MP{mp_no}_Direction'])

        # Compute MP width/length (from SEM procedure)
        target_cd_pixel = self.eps_data[f'MP{mp_no}_TargetCD'] * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
        # Limit search area to 30 pixels
        # TODO: handle NaN & pitch (SA_out) # TODO check box overlap vs targetCD (SA_in)
        self.eps_data[f'MP{mp_no}_SA_In'] = (target_cd_pixel / 3).fillna(500).astype(int).clip(upper=30)
        self.eps_data[f'MP{mp_no}_SA_Out'] = self.eps_data[f'MP{mp_no}_SA_In']
        self.eps_data[f'MP{mp_no}_MeaLeng'] = measleng or self.meas_len  # TODO: compute vs height  # FIXME same value = 100 ???
        # if not self.eps_data['MP2_X']:
        self.eps_data['MP1_PNo'] = self.eps_data['EPS_ID']  # TODO not for multiple MP
        # else: handle if needed
        # self.eps_data[f'MP{mp_no}_Template'] = template
        # FIXME right place ? right code ?
        # fonctionnality for the ODIFF3 recipe of élodie.s
        if isinstance(self.json_conf['mp_template'], str):
            self.eps_data[f'MP{mp_no}_Template'] = self.json_conf['mp_template']
        elif isinstance(self.json_conf['mp_template'], dict):
            self.eps_data[f'MP{mp_no}_Template'] = self.core_data['1D/2D'].apply(lambda x: self.json_conf['mp_template']['1D']
                                                                                 if x == '1D'
                                                                                 else (self.json_conf['mp_template']['2D']
                                                                                       if x == '2D' else ''))

    def mapping_from_fix_values(self) -> None:
        for csv_col, value in self.FIXED_VALUES.items():
            self.eps_data[csv_col] = value

    def mapping_from_df(self) -> None:
        """Map columns from core dataframe to target HSS naming"""
        for csv_col, gauge_col in self.MAPPING.items():
            self.eps_data[csv_col] = self.core_data[gauge_col]

    def mapping_core_data(self) -> None:
        for csv_col, value_user_input in self.MAPPING_CORE_DATA.items():
            if self.json_conf[value_user_input] != "":
                self.eps_data[csv_col] = self.json_conf[value_user_input]
            elif csv_col in self.FIXED_VALUES and self.json_conf[value_user_input] == "":
                self.eps_data[csv_col] = self.FIXED_VALUES[csv_col]
            else:
                print(f"/!\ {csv_col} is not specified in user_config.json. Make sure there is a default value for this column")
                pass

    # method naming based on Hitachi doc
    def set_eps_data_id(self) -> None:
        # __________EPS_ID section__________
        self.eps_data['EPS_ID'] = range(1, min(len(self.core_data) + 1, 9999))
        if any(id > 9999 for id in self.eps_data['EPS_ID']):
            raise ValueError("EPS_ID values cannot exceed 9999")

    def set_eps_data_eps_modification(self) -> None:
        # from eps_name to fer_eps_id
        # EPS_Name is mapped
        # Ref_EPS_ID has default template value
        pass

    def set_eps_data_template(self) -> None:
        # from eps_template to ep_template
        # __________EPS_Template section__________
        # self.eps_data['EP_Template'] = dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step]
        self.eps_data['EP_Template'] = dict(PH="banger_EP_F16", ET="banger_EP_F32", PH_HR="template_EP_F16_HR",
                                            ET_HR="template_EP_F32_HR")[self.step]

    def set_eps_data_ap1_modification(self) -> None:
        # from type to AP1_AST_Mag
        pass

    def set_eps_data_ap2_modification(self) -> None:
        # from type to AP2_AST_Mag
        # AP1_Mag, AP1_Rot, AP1_AF_Mag are mapped
        pass

    def set_eps_data_ep_modification(self) -> None:
        """Columns from EP_Mag_X to EP_ABCC_X"""
        # __________EP_Rot section__________
        # TODO auto-rotation en fonction de plusieurs MP ? # FIXME demander a Julien + Mode
        self.eps_data["EP_Rot"] = np.where(self.core_data.orientation == "x", 0, 90)
        # EP_AF_X, EP_AF_Y
        pass

    def fill_type_in_eps_data(self) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        # FIXME overriding fix values ???
        for col in self.eps_data:
            if col == "Type1":
                self.eps_data[col] = 1
            # FIXME maintenabilité : 11 dépends du nommage et de la place de la colonne Type11 dans le template  # noqa E501
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 12:
                self.eps_data[col] = 2

    def get_eps_data(self) -> pd.DataFrame:
        '''callable method (destination HssCreator) which returns the EPS_Data dataframe containing the values'''
        print('3. <EPS_Data> section creation')  # to log
        self.mapping_from_fix_values()
        self.mapping_from_df()
        self.mapping_core_data()
        self.set_eps_data_id()
        self.add_mp_width(1)  # TODO make it dynamic ?
        self.set_eps_data_eps_modification()
        self.set_eps_data_template()
        self.set_eps_data_ap1_modification()
        self.set_eps_data_ap2_modification()
        self.set_eps_data_ep_modification()
        self.fill_type_in_eps_data()
        if not self.eps_data.empty:  # better check + log
            print('\t<EPS_Data> created')
        return self.eps_data
