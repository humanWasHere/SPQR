import logging
from enum import Flag
from typing import Literal, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Tone(Flag):
    """Tones of layout features, reticle field, and photoresist."""
    LINE = 0
    SPACE = 1
    CLEAR = 0
    DARK = 1
    PTD = 0
    NTD = 1


def combine_tones(pattern: Tone, mask_field: Tone, resist: Tone = Tone.PTD) -> Tone:
    """Combine tones using XOR to return resist LINE or SPACE"""
    return Tone(pattern ^ mask_field ^ resist)


class EPSData:
    """Manage the creation of a DataFrame for EPS_Data only, computed from core data"""
    # mapping in which the values are values to write in the recipe (since they are fixed)
    FIXED_VALUES = {
        'Mode': 1,
        'EPS_Template': "EPS_Default",
        'AP2_Template': "OPC_AP2_Off",
        'AP1_Mag': 45000,  # TODO: coherence Template
        'AP1_AF_Mag': 45000,
        'AP1_Rot': 0,
    }

    # mapper which matches the values of 2 different dataframes
    MAPPING_COREDATA = {
        'EPS_Name': "name",
        'Move_X': "x",
        'Move_Y': "y",
        'EP_AF_X': "x_ap",
        'EP_AF_Y': "y_ap",
        'AP1_X': "x_ap",
        'AP1_Y': "y_ap",
        'AP1_AF_X': "x_ap",
        'AP1_AF_Y': "y_ap",
    }

    # mapper which matches the values of 2 different dataframes
    MAPPING_TEMPLATES = {
        'EP_Template': "ep_template",
        'EPS_Template': "eps_template",
        'AP1_Template': "ap1_template",
    }

    def __init__(self, core_data: pd.DataFrame, step: str, mag: int, ap_mag: int, templates: dict,
                 eps_columns: pd.DataFrame, field_tone: str = "clear"):
        # TODO: validate data (columns, type, nan...) -> validator -> see when to validate in flow
        self.core_data = core_data.astype(dict(x=int, y=int, x_ap=int, y_ap=int), errors="ignore")
        assert step in {"PH", "ET", "PH_HR", "ET_HR"}
        self.step = step
        self.mag = mag
        self.ap_mag = ap_mag
        self.templates = templates
        # self.columns = columns  # {'eps_col': value} similar to FIXED_VALUES mapper -> use it?
        self.eps_data = pd.DataFrame(columns=eps_columns.columns)
        self.field_tone = Tone[field_tone.upper()]

    def add_mp_width(self, mp_no=1, direction: Optional[Literal['X', 'Y']] = None,
                     template: str = "", measleng: int = 100) -> None:
        """Add one width measurement point (line/space depending on MP template) at image center"""
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
        target_cd_pixel = (self.eps_data[f'MP{mp_no}_TargetCD']
                           * self.eps_data.EP_Mag_X * 512 / 1000 / 135000)
        # Limit search area to 30 pixels
        # TODO: handle NaN & pitch (SA_out) # TODO check box overlap vs targetCD (SA_in)
        self.eps_data[f'MP{mp_no}_SA_In'] = (target_cd_pixel / 3).fillna(500).astype(int).clip(upper=30)
        self.eps_data[f'MP{mp_no}_SA_Out'] = self.eps_data[f'MP{mp_no}_SA_In']
        self.eps_data[f'MP{mp_no}_MeaLeng'] = measleng  # TODO: compute measlen vs height
        self.eps_data['MP1_PNo'] = self.eps_data['EPS_ID']  # TODO not for multiple MP

        # MP_Template according to CD/SPACE in self.core_data
        self.eps_data[f'MP{mp_no}_Template'] = template or self.get_mp_template()

    def get_mp_template(self) -> pd.Series:
        template = self.templates['mp_template']
        if isinstance(template, str):
            return pd.Series([template] * len(self.core_data))

        # Column operations to apply resist line or space template
        polygon: pd.Series = self.core_data['polygon_tone'].apply(Tone.__getitem__)
        resist = polygon.apply(combine_tones, args=(self.field_tone,))

        if not template:
            return np.where(resist == Tone.LINE, "Width_Default", "Space_Default")
        if isinstance(template, dict) and list(template.keys()) == ['line', 'space']:
            return np.where(resist == Tone.LINE, template['line'], template['space'])

        # FIXME 1D/2D is not in spec: to deprecate
        if isinstance(template, dict) and list(template.keys()) == ['1D', '2D']:
            return np.where(self.core_data['1D/2D'] == '1D', template['1D'],
                            np.where(self.core_data['1D/2D'] == '2D', template['2D'], template))

    def mapping_core_data(self) -> None:
        """Map columns from core dataframe to target HSS naming"""
        for eps_col, core_col in self.MAPPING_COREDATA.items():
            self.eps_data[eps_col] = self.core_data[core_col]

    def mapping_from_fix_values(self) -> None:
        """Fill default value for entire columns"""
        for eps_col, value in self.FIXED_VALUES.items():
            self.eps_data[eps_col] = value

    def mapping_user_config(self) -> None:
        """Fill columns with user input from JSON config (overwrites fixed values)"""
        self.eps_data[['EP_Mag_X', 'EP_AF_Mag']] = self.mag
        if self.ap_mag:
            self.eps_data[['AP1_Mag', 'AP1_AF_Mag']] = self.ap_mag
        for eps_col, user_col_key in self.MAPPING_TEMPLATES.items():
            if self.templates[user_col_key] != "":
                self.eps_data[eps_col] = self.templates[user_col_key]
            elif eps_col in self.FIXED_VALUES:  # not needed if fix_values executed before
                self.eps_data[eps_col] = self.FIXED_VALUES[eps_col]
            else:
                logger.warning(f"{eps_col} is not specified in user_config.json. "
                               "Make sure there is a default value for this column")

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
        # __________EP_Template section__________
        if self.templates['ep_template'] == "":
            self.eps_data['EP_Template'] = dict(
                PH="banger_EP_F16",
                ET="banger_EP_F32",
                PH_HR="banger_EP_F16",
                ET_HR="banger_EP_F32")[self.step]
        else:
            self.eps_data['EP_Template'] = self.templates['ep_template']

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
        self.eps_data["EP_Rot"] = np.where(self.core_data.orientation.str.lower() == "x", 0, 90)
        # EP_AF_X, EP_AF_Y
        pass

    def fill_type_in_eps_data(self) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        for col in self.eps_data.columns:
            if col == "Type1":
                self.eps_data[col] = 1
            # FIXME rework for dynamic MPs
            elif col.startswith("Type") and int(col[4:6]) < 12:
                self.eps_data[col] = 2

    def get_eps_data(self) -> pd.DataFrame:
        """Return the EPS_Data dataframe in HSS format for HSScreator"""
        logger.info('3. <EPS_Data> section creation')
        # Do not change order, EPS_ID/EPS_Name should be initialized first
        self.mapping_core_data()
        self.mapping_from_fix_values()
        self.mapping_user_config()
        self.set_eps_data_id()
        self.add_mp_width(1)  # TODO make it dynamic ?
        self.set_eps_data_eps_modification()
        self.set_eps_data_template()
        self.set_eps_data_ap1_modification()
        self.set_eps_data_ap2_modification()
        self.set_eps_data_ep_modification()
        self.fill_type_in_eps_data()
        if not self.eps_data.empty:
            logger.info('<EPS_Data> created')
        return self.eps_data
