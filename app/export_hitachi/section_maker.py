import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class SectionMaker:
    """
    This class is used to create, fill or modify the values of all HSS sections except EPS_Data
    Values are modified in-place. If not modified, value is set to default as in template.json
    """

    def __init__(self, df_dict: dict[str, pd.DataFrame]):
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
        self.recipe = df_dict["<Recipe>"]
        self.measenv_exec = df_dict["<MeasEnv_Exec>"]
        self.measenv_measres = df_dict["<MeasEnv_MeasRes>"]

    def make_gp_data_section(self) -> pd.DataFrame:
        """Set gp data section by calculation or definition"""
        # __________GP_ID section__________
        # # preventing data to be out of range -> match doc
        # if any(id > 10 for id in self.gp_data['GP_ID']):
        #     raise ValueError("GP_ID values cannot exceed 10")
        # __________Type column checks__________
        if self.gp_data['Type'].ne(1).any():
            logger.warning(f"ValueError: <GP_Data>Type should be 1")
            # raise ValueError("<GP_Data>Type should be 1")

        # __________GP_Template coolumn checks__________
        # dynamic assignation of GP_Template
        if self.gp_data["GP_Template"].isna().any():
            logger.warning(f"ValueError: <GP_Data>GP_Template is mandatory")
            # raise ValueError("<GP_Data>GP_Template is mandatory")

        # __________GP_Mag column checks__________
        gp_template = self.gp_data["GP_Template"]
        om_template_rows = gp_template.str.contains("OM")
        sem_template_rows = gp_template.str.contains("SEM")
        assert self.gp_data.loc[om_template_rows, "GP_Mag"].isin([104, 210]).all(), \
            "GP_MAG for OM should be either 104 or 210"
        assert self.gp_data.loc[sem_template_rows, "GP_Mag"].between(1000, 500_000).all(), \
            "GP_MAG for SEM should be between 1000 and 500000"

        # __________GP_ROT section__________
        return self.gp_data

    def make_idd_cond_section(self, layout: str, topcell: str) -> pd.DataFrame:
        self.idd_cond.loc[0, ["DesignData", "CellName"]] = Path(layout).stem, topcell
        return self.idd_cond

    def make_idd_layer_data_section(self, mask_layer: int, tone: str) -> pd.DataFrame:
        """Set IDD_Layer_Data section for visible layer mapping"""
        # TODO link with step / target layer
        self.idd_layer_data.loc[0, ['LayerNo', 'DataType']] = 0, 114
        self.idd_layer_data.loc[1:, 'LayerNo'] = mask_layer
        self.idd_layer_data.loc[:, 'Tone'] = dict(clear=0, dark=1)[tone]
        return self.idd_layer_data

    def make_recipe_section(self, step: str) -> pd.DataFrame:
        #  __________SEMCondNo__________
        step_to_value = dict(PH=2, ET=1, PH_HR=11, ET_HR=13)
        if step not in step_to_value.keys():
            logger.warning(f"ValueError: Step not in {', '.join(step_to_value.keys())}.")
            # raise ValueError(f"Supported steps are {', '.join(step_to_value.keys())}.")
        self.recipe["SEMCondNo"] = step_to_value[step]
        return self.recipe

    # By default, each section returns the default value from the JSON template

    def make_coordinate_system_section(self) -> pd.DataFrame:
        """Set coordinate system section by calculation or definition"""
        return self.coordinate_system

    def make_epa_list_section(self) -> pd.DataFrame:
        return self.epa_list

    def make_gp_coordinate_system_section(self) -> pd.DataFrame:
        return self.gp_coordinate_system

    def make_gp_offset_section(self) -> pd.DataFrame:
        return self.gp_offset

    def make_gpa_list_section(self) -> pd.DataFrame:
        return self.gpa_list

    def make_image_env_section(self) -> pd.DataFrame:
        return self.image_env

    def make_measenv_exec_section(self) -> pd.DataFrame:
        return self.measenv_exec

    def make_measenv_measres_section(self) -> pd.DataFrame:
        return self.measenv_measres

    def make_unit_section(self) -> pd.DataFrame:
        return self.unit
