import numpy as np
import pandas as pd


class HssInterface:
    STR_DICT = {
        '<FileID>': 'LIDP00'
    }
    DF_DICT = {
        '<GP_List>': pd.DataFrame(),
        '<EPS_Data>': pd.DataFrame()
    }

    def __init__(self, json_template: str, df_epsdata: pd.DataFrame):
        with open(json_template, "r") as f:
            self.json_template = json.load(f)
        self.string_dict = {}
        self.dataframe_dict = {'<EPS_Data>': df_epsdata}
        
    def to_dataframes(self):
        for key, value in self.header.items():
            if isinstance(value, dict):
                # si dictionnaire de listes
                self.dataframe_dict[key] = pd.DataFrame(value)
                pd.read_json()?
                # si chaines de caracteres
                self.dataframe_dict[key] = pd.DataFrame(value, index=[0])
            else:
                self.string_dict[key] = value
    
    def contat_to_csv(self):
        # normaliser largeur des dataframes
        max_width = ...
        for self.dataframe_dict.values():
            # (ajouter des colonnes vides pour correspondr à la largeur max)
            # (ajouter des lignes pour les noms de section ? <GP_Data>)
            df.to_csv()
        # concatener les csv
        full_dataframe.fillna('').to_csv(index=False, header=False)

# class DataFrameConverter:
#     input_dataframe
#     output_dataframe
# class DataFrameToEPSData(DataFrameConverter):


class DataFrameToEPSData:
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
    MAP = {
        'Move_X': "x",
        'Move_Y': "y",
        'EPS_Name': "name",
        'AP1_X': "x_ap_rel",
        'AP1_Y': "y_ap_rel",
        'AP1_AF_X': "x_ap_rel",
        'AP1_AF_Y': "y_ap_rel",
        'EP_Mag_X': "mag",
        'EP_AF_X': "x_af_rel",
        'EP_AF_Y': "y_af_rel",
        'EP_AF_Mag': "mag",
        'MP1_Name': "name",
        'MP1_TargetCD': "target_cd",
        'MP1_Direction': "orient"
    }

    header = ''

    def __init__(self, gauges: pd.DataFrame, step : str = "PH"):
        EPS_COLUMNS = json_template['<EPS_Data>'].keys()  #TODO
        # make Type column names unique
        header = [label + str(i) if label == "Type" else label for i, label in enumerate(EPS_COLUMNS)]

        #TODO:  validate data (columns, dtype, nan...)        
        self.gauges = gauges  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame(columns=header)
        assert step in {"PH", "ET"}
        self.step = step

        self.init_columns()
        self.map_columns()
        self.autofill_columns()

    def set_rotation(self):
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90

        rot = np.where(self.eps_data['MP1_Direction'] == "X", 0, 90)
        # elif Y
        return rot

    def test(self):
        TEST_MAPPING = {
            'Mode': 1,
            'EPS_Template': "EPS_Default",
            'AP2_Template': "OPC_AP2_Off",
            'AP1_Mag': 45000,
            'AP1_AF_Mag': 45000,
            'AP1_Rot': 0,
            'MP1_X': 0,
            'MP1_Y': 0,
            'Move_X': self.gauges["x"],
            'Move_Y': self.gauges["y"],
            'EP_Template': dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step],
            'EP_Rot': self.set_rotation()
        }

    def init_columns(self):
        """Generate unique IDs and fill columns with default values"""
        self.eps_data['#EPS_ID'] = range(1, self.gauges.shape[0] + 1)
        self.eps_data['MP1_PNo'] = self.eps_data['#EPS_ID']
        for csv_col, value in self.DEFAULTS.items():
            self.eps_data[csv_col] = value

    def map_columns(self):
        """Map gauge dataframe columns with corresponding recipe columns without further processing"""
        for csv_col, gauge_col in self.MAP.items():
            self.eps_data[csv_col] = self.gauges[gauge_col]

    def autofill_columns(self):
        """Fill more columns using logic"""
        self.eps_data['EP_Template'] = dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step]

        # Set rotation
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90
        # Compute measure point width/length (from SEM procedure)
        # TODO: MP_Cursor_Size_X/Y etc. for Ellipse. cf doc HSS p. 67
        search_area = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000 / 3
        # cursor_size = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
        # Limit search area to 30 pixels / todo: handle NaN
        self.eps_data['MP1_SA_In'] = self.eps_data['MP1_SA_Out'] = search_area.fillna(500).astype(int).clip(upper=30)
        self.eps_data['MP1_MeaLeng'] = self.measleng  # TODO: compute
        # Fill Type columns. First one is 1, all others are 2 (?)
        type_cols = [i for i, label in enumerate(EPS_COLUMNS[:65]) if label == "Type"]  # list of column indices  #TODO 65 for 1 MP, 66 for 2 MP...
        self.eps_data.iloc[:, type_cols] = 2
        self.eps_data.iloc[:, 1] = 1