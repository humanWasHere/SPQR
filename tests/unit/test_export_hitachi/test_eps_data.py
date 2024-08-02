import json
from pathlib import Path

import pandas as pd
import pytest

from app.export_hitachi.eps_data import EPSData


class TestEpsData:

    @pytest.fixture
    def eps_data_columns(self) -> dict:
        test_hss = Path(__file__).resolve().parents[2] / "testfiles" / "test_template.json"
        hss_template = json.loads(test_hss.read_text())
        return pd.DataFrame(columns=hss_template.get('<EPS_Data>'))

    @pytest.fixture
    def eps_data_instance(self, eps_data_columns) -> EPSData:
        data_instance = pd.DataFrame({'name': ['gauge1', 'gauge2', 'gauge3'],
                                      'x': [10, 20, 30],
                                      'y': [100, 200, 300],
                                      'x_ap': [10, 20, 30],
                                      'y_ap': [30, 20, 10],
                                      'x_dim': [3000, 3000, 3000],
                                      'y_dim': [3000, 3000, 3000],
                                      'orientation': ['Y', 'Y', 'Y']})
        template_config = {
            "ap1_template": "",
            "ep_template": "",
            "eps_template": "EPS_Template",
            "mp_template": "X90M_GATE_PH",
        }
        test_ex_gauge_df = EPSData(core_data=data_instance, step='PH', mag=200000, ap_mag=50000,
                                   templates=template_config, eps_columns=eps_data_columns)
        return test_ex_gauge_df

    def test_add_mp_width(self, eps_data_instance):
        '''checks wether add_mp_width method fills data as expected'''
        # Arrange
        eps_data_instance.eps_data['EP_Mag_X'] = [200000, 200000, 200000]  # needed for target_cd definition
        eps_data_instance.eps_data['EPS_ID'] = [1, 2, 3]  # needed for MP_ID
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
        columns_to_check = ['EP_Mag_X', 'EPS_ID', 'MP1_X', 'MP1_Y', 'MP1_TargetCD', 'MP1_Direction', 'MP1_Name', 'MP1_SA_In', 'MP1_SA_Out', 'MP1_MeaLeng', 'MP1_PNo', 'MP1_Template']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_data)

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
        columns_to_check = ['EPS_Name', 'Move_X', 'Move_Y', 'EP_AF_X', 'EP_AF_Y', 'AP1_X', 'AP1_Y', 'AP1_AF_X', 'AP1_AF_Y']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_data)

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
        columns_to_check = ['EPS_Name', 'Mode', 'EPS_Template', 'AP2_Template', 'AP1_Mag', 'AP1_AF_Mag', 'AP1_Rot']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        for column, value in EPSData.FIXED_VALUES.items():
            assert (eps_data_instance_eps_data_subset[column] == value).all(), f"Column {column} does not match fixed value {value}"
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_eps_data_df)

    def test_mapping_user_config(self, eps_data_instance):
        # Arrange
        eps_data_instance.eps_data['EPS_ID'] = [1, 2, 3]  # indexes the df
        expected_data = pd.DataFrame({'EPS_ID': [1, 2, 3],
                                      'EP_Mag_X': [200000, 200000, 200000],
                                      'EP_AF_Mag': [200000, 200000, 200000],
                                      'AP1_Mag': [50000, 50000, 50000],
                                      'EPS_Template': ["EPS_Template", "EPS_Template", "EPS_Template"],
                                      })

        # Act
        eps_data_instance.mapping_user_config()
        columns_to_check = ['EPS_ID', 'EP_Mag_X', 'EP_AF_Mag', 'AP1_Mag', 'EPS_Template']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_data)

    def test_set_eps_data_id(self, eps_data_instance):
        '''checks wether setting EPS_ID data setting iterativelly works'''
        # Arrange
        expected_eps_data_df = pd.DataFrame({'EPS_ID': [1, 2, 3]})

        # Act
        eps_data_instance.set_eps_data_id()
        columns_to_check = ['EPS_ID']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_eps_data_df)

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
        columns_to_check = ['EPS_Name', 'EP_Template']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_eps_data_df)

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
        columns_to_check = ['EP_Rot']
        eps_data_instance_eps_data_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        pd.testing.assert_frame_equal(eps_data_instance_eps_data_subset, expected_eps_data_df)

    # TODO
    def test_fill_type_in_eps_data(self, eps_data_instance: EPSData):
        '''checks for types sections (correct number)'''
        # Act
        eps_data_instance.eps_data['EP_Mag_X'] = [200000, 200000, 200000]  # needed for target_cd definition
        eps_data_instance.eps_data['EPS_ID'] = [1, 2, 3]  # needed for MP_ID
        eps_data_instance.eps_data[[f'Type{i}' for i in range(1, 15)]] = None

        eps_data_instance.fill_type_in_eps_data()

        # Assert
        assert eps_data_instance.eps_data['Type1'].eq(1).all()
        for i in range(2, 11):
            assert eps_data_instance.eps_data[f'Type{i}'].eq(2).all()
        # From Type column 11, filled with 2 only if following MP is added
        assert eps_data_instance.eps_data['Type11'].eq(2).all()
        # TODO
        # assert eps_data_instance.eps_data['Type11'].isna().all()
        # eps_data_instance.add_mp_width()
        # eps_data_instance.fill_types()
        # assert eps_data_instance.eps_data['Type11'].eq(2).all()

        for i in range(12, 15):
            assert eps_data_instance.eps_data[f'Type{i}'].isna().all()

    def test_get_eps_data(self, eps_data_instance):
        '''checks wether whole eps_data data setting works as expected'''
        # Arrange
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
                                         'AP1_AF_Mag': [50000, 50000, 50000],
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
        columns_to_check = ['EPS_Name', 'Move_X', 'Move_Y', 'EP_AF_X', 'EP_AF_Y', 'AP1_X', 'AP1_Y', 'AP1_AF_X', 'AP1_AF_Y', 'Mode', 'EPS_Template', 'AP2_Template', 'AP1_Mag', 'AP1_AF_Mag',
                            'AP1_Rot', 'EP_Mag_X', 'EP_AF_Mag', 'EPS_ID', 'MP1_X', 'MP1_Y', 'MP1_TargetCD', 'MP1_Direction', 'MP1_Name', 'MP1_SA_In', 'MP1_SA_Out', 'MP1_MeaLeng', 'MP1_PNo', 'MP1_Template', 'EP_Template', 'EP_Rot']
        result_subset = eps_data_instance.eps_data[columns_to_check]

        # Assert
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result_subset, expected_data_df)
