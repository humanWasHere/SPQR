import json
from pathlib import Path

import pandas as pd
import pytest

from app.export_hitachi.eps_data import EPSData


class TestEpsData:

    @pytest.fixture
    def eps_data_columns(self) -> dict:
        test_hss = Path(__file__).resolve().parents[1] / "testfiles" / "test_template.json"
        hss_template = json.loads(test_hss.read_text())
        return hss_template.get('<EPS_Data>')

    @pytest.fixture
    def eps_data_instance(self, eps_data_columns):
        data_instance = pd.DataFrame({'name': ['gauge1', 'gauge2', 'gauge3'],
                                      'x': [10, 20, 30],
                                      'y': [100, 200, 300],
                                      'x_ap': [10, 20, 30],
                                      'y_ap': [30, 20, 10],
                                      'x_dim': [3000, 3000, 3000],
                                      'y_dim': [3000, 3000, 3000],
                                      'orientation': ['Y', 'Y', 'Y']})
        test_json_user_config = {
            "recipe_name": "test_env_genepy",
            "output_dir": "/work/opc/all/users/chanelir/semrc/recipe_output/test_env",
            "parser": "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt",
            "layout": "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds",
            "layers": ["1.0"],
            "ap1_template": "",
            "ap1_mag": 50000,
            "ep_template": "",
            "eps_template": "EPS_Template",
            "magnification": 200000,
            "mp_template": "X90M_GATE_PH",
            "step": "PH",
            "opcfield_x": "",
            "opcfield_y": "",
            "step_x": "",
            "step_y": "",
            "num_step_x": "",
            "num_step_y": ""
        }
        test_ex_gauge_df = EPSData(core_data=data_instance, user_config_info=test_json_user_config,
                                   step='PH', template={})
        return test_ex_gauge_df

    def test_add_mp_width(self, eps_data_instance):
        '''checks wether add_mp_width method fills data as expected'''
        # Arrange
        eps_data_instance.eps_data['EP_Mag_X'] = [200000, 200000, 200000]  # needed for target_cd definition
        eps_data_instance.eps_data['EPS_ID'] = [1, 2, 3]  # indexes the df
        expected_data = pd.DataFrame({
                                      'EP_Mag_X': [200000, 200000, 200000],
                                      'EPS_ID': [1, 2, 3],
                                      'MP1_X': [0, 0, 0],
                                      'MP1_Y': [0, 0, 0],
                                      'MP1_TargetCD': [3000, 3000, 3000],
                                      'MP1_Direction': ['Y', 'Y', 'Y'],
                                      'MP1_Name': ['gauge1', 'gauge2', 'gauge3'],
                                      'MP1_SA_In': [30, 30, 30],
                                      'MP1_SA_Out': [30, 30, 30],
                                      'MP1_MeaLeng': [100, 100, 100],
                                      'MP1_PNo': [1, 2, 3],
                                      'MP1_Template': ["X90M_GATE_PH", "X90M_GATE_PH", "X90M_GATE_PH"],
                                      })

        # Act
        eps_data_instance.add_mp_width()

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance.eps_data, expected_data)

    def test_mapping_core_data(self, eps_data_instance):
        '''checks wether mapping between 2 dataframe works as expected'''
        # Arrange
        expected_data = pd.DataFrame({'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                                      'Move_X': [10, 20, 30],
                                      'Move_Y': [100, 200, 300],
                                      'EP_AF_X': [10, 20, 30],
                                      'EP_AF_Y': [30, 20, 10],
                                      'AP1_X': [10, 20, 30],
                                      'AP1_Y': [30, 20, 10],
                                      'AP1_AF_X': [10, 20, 30],
                                      'AP1_AF_Y': [30, 20, 10],
                                      })

        # Act
        eps_data_instance.mapping_core_data()

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance.eps_data, expected_data)

    def test_mapping_user_config(self, eps_data_instance):
        # Arrange
        eps_data_instance.eps_data['EPS_ID'] = [1, 2, 3]  # indexes the df
        expected_data = pd.DataFrame({'EPS_ID': [1, 2, 3],
                                      'EPS_Template': ["EPS_Template", "EPS_Template", "EPS_Template"],
                                      'AP1_Mag': [50000, 50000, 50000],
                                      'EP_Mag_X': [200000, 200000, 200000],
                                      'EP_AF_Mag': [200000, 200000, 200000],
                                      })

        # Act
        eps_data_instance.mapping_user_config()

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance.eps_data, expected_data)

    def test_mapping_from_fix_values(self, eps_data_instance):
        '''checks wether assigning data from mapping works as expected'''
        # Arrange
        expected_eps_data_df = pd.DataFrame({
            'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
            'Mode': [1, 1, 1],
            'EPS_Template': ['EPS_Default', 'EPS_Default', 'EPS_Default'],
            'AP2_Template': ['OPC_AP2_Off', 'OPC_AP2_Off', 'OPC_AP2_Off'],
            'AP1_Mag': [45000, 45000, 45000],
            'AP1_AF_Mag': [45000, 45000, 45000],
            'AP1_Rot': [0, 0, 0],
            })

        eps_data_instance.eps_data['EPS_Name'] = ['gauge1', 'gauge2', 'gauge3']

        # Act
        eps_data_instance.mapping_from_fix_values()

        # Assert
        for column, value in EPSData.FIXED_VALUES.items():
            assert (eps_data_instance.eps_data[column] == value).all(), f"Column {column} does not match fixed value {value}"
        pd.testing.assert_frame_equal(eps_data_instance.eps_data, expected_eps_data_df)

    def test_set_eps_data_id(self, eps_data_instance):
        '''checks wether setting EPS_ID data setting iterativelly works'''
        # Arrange
        expected_eps_data_df = pd.DataFrame({'EPS_ID': [1, 2, 3]})

        # Act
        eps_data_instance.set_eps_data_id()

        # Assert
        pd.testing.assert_frame_equal(
            eps_data_instance.eps_data, expected_eps_data_df)

    # def test_set_eps_data_eps_modification(self):
    #     pass

    def test_set_eps_data_template(self, eps_data_instance):
        '''checks wether EP_Template data setting works as expected'''
        # Arrange
        expected_eps_data_df = pd.DataFrame({
            'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
            'EP_Template': ["banger_EP_F16", "banger_EP_F16", "banger_EP_F16"]
            })
        eps_data_instance.eps_data['EPS_Name'] = ['gauge1', 'gauge2', 'gauge3']

        # Act
        eps_data_instance.set_eps_data_template()

        # Assert
        pd.testing.assert_frame_equal(
            eps_data_instance.eps_data, expected_eps_data_df)

    # def test_set_eps_data_ap1_modification(self):
    #     pass

    # def test_set_eps_data_ap2_modification(self):
    #     pass

    def test_set_eps_data_ep_modification(self, eps_data_instance):
        '''checks wether EP_Rot data setting works as expected'''
        # Arrange
        expected_eps_data_df = pd.DataFrame({'EP_Rot': [90, 90, 90]})

        # Act
        eps_data_instance.set_eps_data_ep_modification()

        # Assert
        pd.testing.assert_frame_equal(
            eps_data_instance.eps_data, expected_eps_data_df)

    # TODO
    # retrived from test_hss_creator.py
    # def test_fill_type_in_eps_data(self, hss_instance):
    #     '''checks for types sections (correct number)'''
    #     # Act
    #     hss_instance.fill_type_in_eps_data()

    #     # Assert
    #     # integrates all 4 MPs -> if all 4 MPs, there is 14 types
    #     for i in range(1, 14):
    #         assert f"Type{i}" in hss_instance.table_sections['<EPS_Data>']

    def test_get_eps_data(self, eps_data_instance):
        '''checks wether whole eps_data data setting works as expected'''
        # Arrange
        # FIXME check sa_in with another method

        expected_data_df = pd.DataFrame({'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                                         'Move_X': [10, 20, 30],
                                         'Move_Y': [100, 200, 300],
                                         'EP_AF_X': [10, 20, 30],
                                         'EP_AF_Y': [30, 20, 10],
                                         'AP1_X': [10, 20, 30],
                                         'AP1_Y': [30, 20, 10],
                                         'AP1_AF_X': [10, 20, 30],
                                         'AP1_AF_Y': [30, 20, 10],
                                         'Mode': [1, 1, 1],
                                         'EPS_Template': ["EPS_Template", "EPS_Template", "EPS_Template"],
                                         'AP2_Template': ["OPC_AP2_Off", "OPC_AP2_Off", "OPC_AP2_Off"],
                                         'AP1_Mag': [50000, 50000, 50000],
                                         'AP1_AF_Mag': [45000, 45000, 45000],
                                         'AP1_Rot': [0, 0, 0],
                                         'EP_Mag_X': [200000, 200000, 200000],
                                         'EP_AF_Mag': [200000, 200000, 200000],
                                         'EPS_ID': [1, 2, 3],
                                         'MP1_X': [0, 0, 0],
                                         'MP1_Y': [0, 0, 0],
                                         'MP1_TargetCD': [3000, 3000, 3000],
                                         'MP1_Direction': ['Y', 'Y', 'Y'],
                                         'MP1_Name': ['gauge1', 'gauge2', 'gauge3'],
                                         'MP1_SA_In': [30, 30, 30],
                                         'MP1_SA_Out': [30, 30, 30],
                                         'MP1_MeaLeng': [100, 100, 100],
                                         'MP1_PNo': [1, 2, 3],
                                         'MP1_Template': ['X90M_GATE_PH', 'X90M_GATE_PH', 'X90M_GATE_PH'],
                                         'EP_Template': ["banger_EP_F16", "banger_EP_F16", "banger_EP_F16"],
                                         'EP_Rot': [90, 90, 90],
                                         })
        # TODO add MPs ?

        # Act
        result = eps_data_instance.get_eps_data()
        print(result.columns)
        print(expected_data_df.columns)

        # Assert
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected_data_df)
