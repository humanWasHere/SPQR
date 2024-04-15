import tempfile
import pandas as pd
from pathlib import Path
from ..interfaces.calibre_python import lance_script
# from pyrat.DesignControler import DesignControler
# from pyratImplementation.GTCheck.GTCheckService import GTcheckError

# TODO change path access if code is running on prod serv
# does it closes the temp file ?
# Warning Path must be str not Path file


class Measure:
    def __init__(self, parser_input: pd.DataFrame, layout: str | Path, layers: list, precision: int, tcl_script=None, unit="nm"):  # TODO should work with dbu ?
        if tcl_script is None:
            self.tcl_script = Path(__file__).parent / "measure.tcl"
            if not self.tcl_script.exists():
                raise FileNotFoundError(f"Could not find {self.tcl_script}")
        self.parser_df = parser_input
        self.x_y_points = parser_input[['name', 'x', 'y']]
        self.layout = layout
        self.layers = layers  # target_layers
        self.unit = unit
        self.precision = precision

    def creation_script_tmp(self, output, search_area=5) -> Path:
        '''this method creates a temporary script using a TCL script template and input data'''
        # TODO this method should close temp file ?
        # TODO rationnaliser l'emplacement des fichiers temporaires
        # Place temporary script in user's home because /tmp is not shared across farm
        tmp_script = Path.home() / "tmp" / "Script_tmp.tcl"
        # tmp_script = tempfile.NamedTemporaryFile(suffix=".tcl", dir=Path.home()/"tmp")  # gets deleted out of scope?

        # self.precision = int(float(self.layout_peek("precision")))

        # precision = DesignControler(layout).getPrecisionNumber()  # raises GTcheckError
        correction = {'um': 1, 'nm': 1000, 'dbu': self.precision}
        # Format coordinates as [{name x y}, ...]
        coordonnees = [
            f"{{{' '.join(row.astype(str).tolist())}}}" for _, row in self.x_y_points.iterrows()]

        with open(self.tcl_script, "r", encoding="utf-8") as template, open(tmp_script, "w") as script:
            texte = template.read()
            texte = texte.replace("FEED_ME_LAYER", ' '.join(self.layers))
            texte = texte.replace("FEED_ME_SEARCH_AREA", str(search_area))
            texte = texte.replace("FEED_ME_PRECISION", str(self.precision))
            texte = texte.replace("FEED_ME_CORRECTION", str(correction[self.unit]))
            texte = texte.replace("FEED_ME_COORDINATES", '\n'.join(coordonnees))
            texte = texte.replace("FEED_ME_GDS", self.layout)
            texte = texte.replace("FEED_ME_OUTPUT", output)
            script.write(texte)
        return tmp_script

    def process_results(self, output_path) -> pd.DataFrame:
        meas_df = pd.read_csv(output_path, index_col=False, na_values="unknown")
        # TODO : traiter les "Pitch non symetrical" -> minimum?
        meas_df.dropna(subset=[" X_dimension(nm) ", " Y_dimension(nm) "], inplace=True)  # invalid rows
        # TODO : rename in tcl file?
        meas_df.rename(columns={'Gauge ': "name", ' X_dimension(nm) ': "x_dim", ' Y_dimension(nm) ': "y_dim",
                                'pitch_x(nm)': "pitch_x", 'pitch_y(nm)': "pitch_y", ' Polarity (polygon) ': "polarity"},
                       inplace=True)
        meas_df.loc[meas_df.x_dim == 0, "x_dim"] = 3000  # FIXME measure out of range?
        meas_df.y_dim.replace(to_replace=0, value=3000, inplace=True)
        # # TODO doublon avec dataframe_to_eps.add_mp  / a decoupler ?
        # meas_df['target_cd'] = meas_df[['x_dim', 'y_dim']].min(axis=1)
        # meas_df.loc[meas_df.target_cd == meas_df.y_dim, 'orient'] = 'Y'
        # meas_df.loc[meas_df.target_cd == meas_df.x_dim, 'orient'] = 'X'
        return meas_df

    def run_measure(self) -> pd.DataFrame:
        '''runs Calibre script to automatically measure a layout'''
        measure_tempfile = tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[2] / ".temp")
        # TODO where to store tmp files (script + results)
        measure_tempfile_path = measure_tempfile.name
        tmp = self.creation_script_tmp(measure_tempfile_path)
        print('2. measurement')  # TODO log
        lance_script(tmp, verbose=True)
        # (Path(__file__).resolve().parents[2] / "recipe_output" / "last_measure.csv").write_text(Path(measure_tempfile_path).read_text())
        meas_df = self.process_results(measure_tempfile_path)

        parser_df = self.parser_df.copy()
        nm_per_unit = {'dbu': 1000/int(float(self.precision)), 'nm': 1, 'micron': 1000}
        parser_df[["x", "y"]] *= nm_per_unit[self.unit]
        try:
            parser_df[["x_ap", "y_ap"]] *= nm_per_unit[self.unit]
        except ValueError:
            pass
        merged_dfs = pd.merge(parser_df, meas_df, on="name")
        # TODO: cleanup columns in merged df
        measure_tempfile.close()  # remove temporary script
        if not merged_dfs.empty:  # more checks + log
            print('\tmeasurement done')
        return merged_dfs