import pytest
import pandas as pd
from app.export_hitachi.eps_data import DataFrameToEPSData
# FIXME is HssCreator needed ?


class TestEpsData:

    @pytest.fixture
    def df_to_eps_data_instance(self):
        data_instance = pd.DataFrame({'name': ['gauge1', 'gauge2', 'gauge3'],
                                      'x': [10, 20, 30],
                                      'y': [100, 200, 300],
                                      'magnification': [200000, 200000, 200000],
                                      'x_ap': [10, 20, 30],
                                      'y_ap': [30, 20, 10],
                                      'x_dim': [3000, 3000, 3000],
                                      'y_dim': [3000, 3000, 3000],
                                      'orientation': ['Y', 'Y', 'Y']})
        test_ex_gauge_df = DataFrameToEPSData(data_instance, "PH")
        return test_ex_gauge_df

    def test_add_mp_width(self):
    #     # TODO

    def test_mapping_from_df(self, df_to_eps_data_instance):
        # Arrange
        # set expected
        expected_data = pd.DataFrame({'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                                      'Move_X': [10, 20, 30],
                                      'Move_Y': [100, 200, 300],
                                      'EP_Mag_X': [200000, 200000, 200000],
                                      'EP_AF_Mag': [200000, 200000, 200000],
                                      'AP1_X': [10, 20, 30],
                                      'AP1_Y': [30, 20, 10],
                                      'AP1_AF_X': [10, 20, 30],
                                      'AP1_AF_Y': [30, 20, 10]})

        # Act
        df_to_eps_data_instance.mapping_from_df()

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data_instance.eps_data, expected_data)

    def test_mapping_from_fix_values(self, df_to_eps_data_instance):
        # Arrange
        # Set expected data
        expected_eps_data_df = pd.DataFrame({
            'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
            'Mode': [1, 1, 1],
            'EPS_Template': ['EPS_Default', 'EPS_Default', 'EPS_Default'],
            'AP2_Template': ['OPC_AP2_Off', 'OPC_AP2_Off', 'OPC_AP2_Off'],
            'Type1': [1, 1, 1],
            'Type2': [2, 2, 2],
            'Type3': [2, 2, 2],
            'AP1_Mag': [45000, 45000, 45000],
            'AP1_AF_Mag': [45000, 45000, 45000],
            'AP1_Rot': [0, 0, 0],
            'MP1_X': [0, 0, 0],
            'MP1_Y': [0, 0, 0]})

        df_to_eps_data_instance.eps_data['EPS_Name'] = ['gauge1', 'gauge2', 'gauge3']

        # Act
        df_to_eps_data_instance.mapping_from_fix_values()

        # print(df_to_eps_data_instance.eps_data)
        # print(expected_eps_data_df)

        # Assert
        for column, value in DataFrameToEPSData.FIXED_VALUES.items():
            assert (df_to_eps_data_instance.eps_data[column] == value).all(), f"Column {column} does not match fixed value {value}"
        pd.testing.assert_frame_equal(df_to_eps_data_instance.eps_data, expected_eps_data_df)

    def test_set_eps_data_id(self, df_to_eps_data_instance):
        # Arrange
        # set expected data
        expected_eps_data_df = pd.DataFrame({'EPS_ID': [1, 2, 3]})

        # Act
        df_to_eps_data_instance.set_eps_data_id()

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data_instance.eps_data, expected_eps_data_df)

        # obj.core_data = pd.DataFrame({'some_column': range(10000)})  # More than 9999 rows

        # # Act & Assert
        # with pytest.raises(ValueError):
        #     obj.generate_eps_id()

    # def test_set_eps_data_eps_modification(self):
    #     pass

    def test_set_eps_data_template(self, df_to_eps_data_instance):
        # Arrange
        # set expected data
        expected_eps_data_df = pd.DataFrame({
            'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
            'EP_Template': ["banger_EP_F16", "banger_EP_F16", "banger_EP_F16"]
            })
        df_to_eps_data_instance.eps_data['EPS_Name'] = ['gauge1', 'gauge2', 'gauge3']

        # Act
        df_to_eps_data_instance.set_eps_data_template()

        print(df_to_eps_data_instance.eps_data)
        print(expected_eps_data_df)

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data_instance.eps_data, expected_eps_data_df)

    # def test_set_eps_data_ap1_modification(self):
    #     # set expected data
    #     expected_eps_data_df = pd.DataFrame({'EP_Template': "banger_EP_F16"})

    #     # Act
    #     df_to_eps_data.set_eps_data_ap1_modification()

    #     # Assert
    #     pd.testing.assert_frame_equal(
    #         df_to_eps_data.eps_data, expected_eps_data_df)

    # def test_set_eps_data_ap2_modification(self):
    #     pass

    def test_set_eps_data_ep_modification(self, df_to_eps_data_instance):
        # Arrange
        # set expected data
        expected_eps_data_df = pd.DataFrame({'EP_Rot': [90, 90, 90]})

        # Act
        df_to_eps_data_instance.set_eps_data_ep_modification()

        print(df_to_eps_data_instance.eps_data)
        print(expected_eps_data_df)

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data_instance.eps_data, expected_eps_data_df)

    def test_get_eps_data(self, df_to_eps_data_instance):
        # Arrange
        # FIXME check sa_in with another method

        expected_data_df = pd.DataFrame({'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                                         'Move_X': [10, 20, 30],
                                         'Move_Y': [100, 200, 300],
                                         'EP_Mag_X': [200000, 200000, 200000],
                                         'EP_AF_Mag': [200000, 200000, 200000],
                                         'AP1_X': [10, 20, 30],
                                         'AP1_Y': [30, 20, 10],
                                         'AP1_AF_X': [10, 20, 30],
                                         'AP1_AF_Y': [30, 20, 10],
                                         'Mode': [1, 1, 1],
                                         'EPS_Template': ["EPS_Default", "EPS_Default", "EPS_Default"],
                                         'AP2_Template': ["OPC_AP2_Off", "OPC_AP2_Off", "OPC_AP2_Off"],
                                         'Type1': [1, 1, 1],
                                         'Type2': [2, 2, 2],
                                         'Type3': [2, 2, 2],
                                         'AP1_Mag': [45000, 45000, 45000],
                                         'AP1_AF_Mag': [45000, 45000, 45000],
                                         'AP1_Rot': [0, 0, 0],
                                         'MP1_X': [0, 0, 0],
                                         'MP1_Y': [0, 0, 0],
                                         'EPS_ID': [1, 2, 3],
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
        # TODO add MPs

        # Act
        result = df_to_eps_data_instance.get_eps_data("X90M_GATE_PH")

        # for col, val in pd.DataFrame(df_to_eps_data_instance).eps_data.items():
        #     for col2, val2 in expected_data_df.items():
        #         if str(val) != str(val2):
        #             print(f"{val} et {val2} ne sont pas semblables pour {col} et {col2}")
        # print(f"gotten : {df_to_eps_data_instance.eps_data['MP1_SA_In']}")
        # print(f"expected : {expected_data_df['MP1_SA_In']}")

        # Assert
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, expected_data_df)
