# import pytest
import pandas as pd
from app.hss_modules.dataframe_to_eps_data import DataFrameToEPSData
# FIXME is HssCreator needed ?


class TestDfToEpsData:

    # @pytest.fixture  # test fixture decorator
    # def df_to_eps_data_instance(self):
    #     return

    # def test_add_mp_width(self):
    #     pass

    def test_mapping_from_df(self):
        # Arrange
        # set logic init
        data_instance = {'name': ['gauge1', 'gauge2', 'gauge3'],
                         'x': [10, 20, 30],
                         'y': [100, 200, 300],
                         'magnification': [200000, 200000, 200000],
                         'x_ap': [10, 20, 30],
                         'y_ap': [30, 20, 10]}
        test_ex_gauge_df = DataFrameToEPSData(pd.DataFrame(data_instance))
        # set expected
        data_expected = {'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                         'Move_X': [10, 20, 30],
                         'Move_Y': [100, 200, 300],
                         'EP_Mag_X': [200000, 200000, 200000],
                         'EP_AF_Mag': [200000, 200000, 200000],
                         'AP1_X': [10, 20, 30],
                         'AP1_Y': [30, 20, 10],
                         'AP1_AF_X': [10, 20, 30],
                         'AP1_AF_Y': [30, 20, 10]}
        expected_data = pd.DataFrame(data_expected)

        # Act
        test_ex_gauge_df.mapping_from_df()

        print(test_ex_gauge_df.eps_data)

        # Assert
        pd.testing.assert_frame_equal(
            test_ex_gauge_df.eps_data, expected_data)

    def test_mapping_from_fix_values(self):
        # Arrange
        # set input data for logic
        # data_instance = {'name': ['gauge1', 'gauge2', 'gauge3'],
        #                  'x': [10, 20, 30],
        #                  'y': [100, 200, 300],
        #                  'magnification': [200000, 200000, 200000],
        #                  'x_ap': [10, 20, 30],
        #                  'y_ap': [30, 20, 10]}

        data_instance = pd.DataFrame()

        df_to_eps_data = DataFrameToEPSData(data_instance)
        # set expected data
        expected_eps_data_df = pd.DataFrame({'Mode': [1, 1, 1],
                                             'EPS_Template': ["EPS_Default", "EPS_Default", "EPS_Default"],
                                             'AP2_Template': ["OPC_AP2_Off", "OPC_AP2_Off", "OPC_AP2_Off"],
                                             'Type1': [1, 1, 1],
                                             'Type2': [2, 2, 2],
                                             'Type3': [2, 2, 2],
                                             'AP1_Mag': [45000, 45000, 45000],
                                             'AP1_AF_Mag': [45000, 45000, 45000],
                                             'AP1_Rot': [0, 0, 0],
                                             'MP1_X': [0, 0, 0],
                                             'MP1_Y': [0, 0, 0]})

        # Act
        df_to_eps_data.mapping_from_fix_values()

        print(df_to_eps_data.eps_data)

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data.eps_data, expected_eps_data_df)

    def test_set_eps_data_id(self):
        data_instance = pd.DataFrame({'name': ['damn', "it's", "a", "test"]})

        df_to_eps_data = DataFrameToEPSData(data_instance)
        # set expected data
        expected_eps_data_df = pd.DataFrame({'EPS_ID': [1, 2, 3, 4]})

        # Act
        df_to_eps_data.set_eps_data_id()

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data.eps_data, expected_eps_data_df)

        # obj.core_data = pd.DataFrame({'some_column': range(10000)})  # More than 9999 rows

        # # Act & Assert
        # with pytest.raises(ValueError):
        #     obj.generate_eps_id()

    # def test_set_eps_data_eps_modification(self):
    #     pass

    def test_set_eps_data_template(self):
        data_instance = pd.DataFrame({'name': ['damn', "it's", "a", "test"]})

        df_to_eps_data = DataFrameToEPSData(data_instance, "PH")
        # set expected data
        expected_eps_data_df = pd.DataFrame({'EP_Template': "banger_EP_F16"})

        # Act
        df_to_eps_data.set_eps_data_template()

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data.eps_data, expected_eps_data_df)

    # def test_set_eps_data_ap1_modification(self):
    #     pass

    # def test_set_eps_data_ap2_modification(self):
    #     pass

    def test_set_eps_data_ep_modification(self):
        data_instance = pd.DataFrame({'name': ['damn', "it's", "a", "test"],
                                      'orientation': 0})

        df_to_eps_data = DataFrameToEPSData(data_instance)
        # set expected data
        expected_eps_data_df = pd.DataFrame({'EP_Rot': "x"})

        # Act
        df_to_eps_data.set_eps_data_ep_modification()

        # Assert
        pd.testing.assert_frame_equal(
            df_to_eps_data.eps_data, expected_eps_data_df)

    def test_get_eps_data(self):
        # Arrange
        data_instance = pd.DataFrame({'name': ['gauge1', 'gauge2', 'gauge3'],
                                      'x': [10, 20, 30],
                                      'y': [100, 200, 300],
                                      'magnification': [200000, 200000, 200000],
                                      'x_ap': [10, 20, 30],
                                      'y_ap': [30, 20, 10]})
        df_to_eps_data = DataFrameToEPSData(data_instance)
        expected_data_df = pd.DataFrame({'EPS_Name': ['gauge1', 'gauge2', 'gauge3'],
                                         'Move_X': [10, 20, 30],
                                         'Move_Y': [100, 200, 300],
                                         'EP_Mag_X': [200000, 200000, 200000],
                                         'EP_AF_Mag': [200000, 200000, 200000],
                                         'AP1_X': [10, 20, 30],
                                         'AP1_Y': [30, 20, 10],
                                         'AP1_AF_X': [10, 20, 30],
                                         'AP1_AF_Y': [30, 20, 10],
                                         'EPS_ID': [1, 2, 3],
                                         'EP_Template': "banger_EP_F16",
                                         'EP_Rot': "x"})
        # TODO add MPs

        # Act
        result = df_to_eps_data.get_eps_data(1)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert result.equals(expected_data_df)
