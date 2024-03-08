# import pytest
import pandas as pd
from app.hss_modules.dataframe_to_eps_data import DataFrameToEPSData
# FIXME is HssCreator needed ?


class TestDfToEpsData:

    # @pytest.fixture  # test fixture decorator
    # def df_to_eps_data_instance(self):
    #     return

    def test_eps_data_mapping(self):
        # Arrange
        # set logic init
        data_instance = {'Gauge name': ['gauge1', 'gauge2', 'gauge3'],
                         'X_coord_Pat': [10, 20, 30],
                         'Y_coord_Pat': [100, 200, 300],
                         ' min_dimension(nm)': [50, 100, 150]}
        test_ex_gauge_df = DataFrameToEPSData(pd.DataFrame(data_instance))
        # set expected
        data_expected = {'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                         'Move_X': [10, 20, 30],
                         'Move_Y': [100, 200, 300],
                         'MP_TargetCD': [50, 100, 150]}
        expected_data = pd.DataFrame(data_expected)

        # Act
        test_ex_gauge_df.eps_data_mapping()

        # Assert
        pd.testing.assert_frame_equal(
            test_ex_gauge_df.eps_data, expected_data)

    def test_global_eps_data_filling(self):
        # Arrange
        # set input data for logic
        data = {'Gauge name': ['gauge1', 'gauge2', 'gauge3'],
                'X_coord_Pat': [10, 20, 30],
                'Y_coord_Pat': [100, 200, 300],
                ' min_dimension(nm)': [50, 100, 150]}
        df_to_eps_data = DataFrameToEPSData(pd.DataFrame(data))
        # set expected data
        expected_eps_data_df = pd.DataFrame({
            "EPS_ID": [1, 2, 3],
            "EP_Template": ['banger_EP_F16', 'banger_EP_F16', 'banger_EP_F16'],
            "MP1_Direction": [1, 1, 1],
            "EP_Rot": [0, 0, 0],
            "Mode": [1, 1, 1]
        })

        # Act
        df_to_eps_data.global_eps_data_filling()

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data.eps_data, expected_eps_data_df)

    def test_get_eps_data(self):
        # Arrange
        data = {'Gauge name': ['gauge1', 'gauge2', 'gauge3'],
                'X_coord_Pat': [10, 20, 30],
                'Y_coord_Pat': [100, 200, 300],
                ' min_dimension(nm)': [50, 100, 150]}
        df_to_eps_data = DataFrameToEPSData(pd.DataFrame(data))
        expected_data_df = pd.DataFrame({'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                                         'Move_X': [10, 20, 30],
                                         'Move_Y': [100, 200, 300],
                                         'MP_TargetCD': [50, 100, 150],
                                         "EPS_ID": [1, 2, 3],
                                         "EP_Template": ['banger_EP_F16', 'banger_EP_F16', 'banger_EP_F16'],
                                         "MP1_Direction": [1, 1, 1],
                                         "EP_Rot": [0, 0, 0],
                                         "Mode": [1, 1, 1]
                                         })

        # Act
        result = df_to_eps_data.get_eps_data()

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert result.equals(expected_data_df)
