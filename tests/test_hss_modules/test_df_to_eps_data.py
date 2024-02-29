import pandas as pd
from ...app.hss_modules.dataframe_to_eps_data import DataFrameToEPSData


class TestDfToEpsData:

    # exemple de test - non pertinent ici
    def test_get_eps_data_returns_expected_data(self):
        # Arrange
        gauges = "work/opc/all/users/chanelir/semrc-project-test/gauges.txt"
        df_to_eps_data_instance = DataFrameToEPSData(gauges=gauges, step="PH")
        expected_data = pd.DataFrame({
            "Gauge": ["Gauge1", "Gauge2", "Gauge3"],
            "Value": [1.0, 2.0, 3.0]
        })

        # Act
        actual_data = df_to_eps_data_instance.get_eps_data()

        # Assert
        assert actual_data.equals(expected_data)