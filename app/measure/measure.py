from pathlib import Path
import tempfile

import pandas as pd
import numpy as np

from ..interfaces.calibre_python import lance_script
from ..data_structure import Block
from ..parsers.parse import FileParser


# TODO change path access if code is running on prod serv
# does it closes the temp file ?


class Measure:
    def __init__(self, parser_input: FileParser, block: Block, layers: list[str],
                 offset: dict = None, tcl_script: str = None, row_range: list = None):
        if offset is None:
            offset = dict(x=0, y=0)
        self.parser_df = parser_input.parse_data()
        self.get_all_intervals(row_range)
        self.unit = parser_input.unit  # TODO should work with dbu ?
        self.layout = block.layout_path
        self.precision = block.precision
        self.layers = layers
        self.offset = offset
        if tcl_script is None:
            tcl_script = Path(__file__).parent / "measure.tcl"
        if not tcl_script.exists():
            raise FileNotFoundError(f"Could not find {tcl_script}")
        self.tcl_script = tcl_script

    def get_all_intervals(self, interval_range) -> None:
        '''modifies self.parser_df to select some intervals of data'''
        if interval_range:
            combined_indices = []
            for interval in interval_range:
                assert interval[0] > 0, "the range selected is out of bound ! Should not be under 1"
                assert interval[1] <= len(self.parser_df), f"the range selected is out of bound ! Should not be above {len(self.parser_df)} for this recipe"
                combined_indices.extend(range(interval[0] - 1, interval[1]))
            self.parser_df = self.parser_df.iloc[combined_indices, :]

    def apply_offset(self):
        # workaround if coords are not in same coord as layout. should be in parser's original unit
        self.parser_df.loc[:, 'x'] += self.offset['x']
        self.parser_df.loc[:, 'y'] += self.offset['y']

    def creation_script_tmp(self, output, search_area=5) -> Path:
        '''this method creates a temporary script using a TCL script template and input data'''
        # TODO this method must close temp file ?
        # TODO rationnaliser l'emplacement des fichiers temporaires
        # Place temporary script in user's home because /tmp is not shared across farm
        tmp_script = Path.home() / "tmp" / "Script_tmp.tcl"
        # tmp_script = tempfile.NamedTemporaryFile(suffix=".tcl", dir=Path.home()/"tmp")
        # gets deleted out of scope?

        # precision = DesignControler(layout).getPrecisionNumber()  # raises GTcheckError
        correction = {'um': 1, 'nm': 1000, 'dbu': self.precision}
        # Format coordinates as [{name x y}, ...]
        coordonnees = (
            self.parser_df.loc[:, ['name', 'x', 'y']]
            .astype({'x': float, 'y': float}).astype(str)
            .apply(lambda row: f"{{{' '.join(row.values)}}}", axis=1)
        )
        # Paths must be passed as str
        with (open(self.tcl_script, "r") as template,
              open(tmp_script, "w") as script):
            texte = template.read()
            texte = texte.replace("FEED_ME_LAYER", ' '.join(self.layers))
            texte = texte.replace("FEED_ME_SEARCH_AREA", str(search_area))
            texte = texte.replace("FEED_ME_PRECISION", str(self.precision))
            texte = texte.replace("FEED_ME_CORRECTION", str(correction[self.unit]))
            texte = texte.replace("FEED_ME_COORDINATES", '\n'.join(coordonnees))
            texte = texte.replace("FEED_ME_GDS", str(self.layout))
            texte = texte.replace("FEED_ME_OUTPUT", output)
            script.write(texte)
        return tmp_script

    def process_results(self, output_path) -> pd.DataFrame:
        meas_df = pd.read_csv(output_path, index_col=False, na_values="unknown")
        # TODO : traiter les "Pitch non symetrical" -> minimum?
        # Drop invalid rows
        meas_df.dropna(subset=[" X_dimension(nm) ", " Y_dimension(nm) "], inplace=True)
        # TODO : rename in tcl file?
        meas_df.rename(columns={'Gauge ': "name", ' X_dimension(nm) ': "x_dim",
                                ' Y_dimension(nm) ': "y_dim", 'pitch_x(nm)': "pitch_x",
                                'pitch_y(nm)': "pitch_y", ' Polarity (polygon) ': "polarity"},
                       inplace=True)
        # FIXME measure out of range? -> modify tcl to handle empty measurement
        meas_df.loc[meas_df.x_dim == 0, "x_dim"] = 3000
        meas_df.replace({'y_dim': {0: 3000}}, inplace=True)
        return meas_df

    def run_measure(self) -> pd.DataFrame:
        '''runs Calibre script to automatically measure a layout'''
        self.apply_offset()
        measure_tempfile = tempfile.NamedTemporaryFile(
            dir=Path.home() / "tmp")
        # TODO where to store tmp files (script + results)
        measure_tempfile_path = measure_tempfile.name
        # measure_tempfile_path = "/work/opc/all/users/chanelir/semrc-outputs/measure_output.csv"
        tmp = self.creation_script_tmp(measure_tempfile_path)
        print('2. Starting measurement')  # TODO log
        lance_script(tmp, verbose=True)
        meas_df = self.process_results(measure_tempfile_path)
        parser_df = self.parser_df.copy()  # FIXME why copy ?
        nm_per_unit = {'dbu': 1000/self.precision, 'nm': 1, 'um': 1000}
        parser_df[["x", "y"]] *= nm_per_unit[self.unit]
        try:
            parser_df[["x_ap", "y_ap"]] *= int(float(nm_per_unit[self.unit]))
        except ValueError:
            pass
        parser_df = parser_df.drop_duplicates(subset=['name'])
        merged_dfs = pd.merge(parser_df, meas_df, on="name")
        # TODO: cleanup columns in merged df
        # print(f"debug cleanup columns measure.py : {merged_dfs.columns.tolist()}")

        # DEBUG copy results CSV
        # results = Path(measure_tempfile_path).read_text()
        # (Path(__file__).parents[2]/"recipe_output"/"measure_output.csv").write_text(results)
        measure_tempfile.close()
        if not merged_dfs.empty:  # more checks + log
            print('\tMeasurement done')
        # print(merged_dfs.columns)
        return merged_dfs
