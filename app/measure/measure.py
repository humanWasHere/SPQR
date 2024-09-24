import logging
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd

from ..data_structure import Block
from ..interfaces.calibre_python import lance_script
from ..parsers.parse import FileParser
logger = logging.getLogger(__name__)

# TODO change path access if code is running on prod serv


class Measure:
    """this class returns a dataframe with measurement information."""
    def __init__(self, parser_input: FileParser, block: Block, layers: list[str],
                 offset: dict | None = None, tcl_script: Optional[str | Path] = None,
                 row_range: Optional[list[list]] = None):

        self.parser_df = parser_input.parse_data()
        self.unit = parser_input.unit  # TODO should work with dbu ?
        self.layout = block.layout_path
        self.precision = block.precision
        self.layers = layers
        if offset is None:
            offset = dict(x=0, y=0)
        self.offset = offset
        if tcl_script is None:
            tcl_script = Path(__file__).parent / "measure.tcl"
            # tcl_script = Path(__file__).parent / "measure_reworked.tcl"
        if not Path(tcl_script).exists():
            raise FileNotFoundError(f"Could not find {tcl_script}")
        self.tcl_script = tcl_script
        if row_range is not None:
            self.get_all_intervals(row_range)

    def get_all_intervals(self, interval_range: list[list]) -> None:
        """modifies self.parser_df to select some intervals of data."""
        # TODO: make it more explicit
        if interval_range:
            combined_indices: list[int] = []
            for interval in interval_range:
                assert interval[0] > 0, "the range selected is out of bound! Should not be under 1"
                assert interval[1] <= len(self.parser_df), f"the range selected is out of bound ! Should not be above {len(self.parser_df)} for this recipe"
                combined_indices.extend(range(interval[0] - 1, interval[1]))
            self.parser_df = self.parser_df.iloc[combined_indices, :]

    def apply_offset(self) -> None:
        """method that applies an offset from configuration file ?
        Not implemented yet."""
        # workaround if coords are not in same coord as layout. should be in parser's original unit
        self.parser_df.loc[:, 'x'] += self.offset['x']
        self.parser_df.loc[:, 'y'] += self.offset['y']

    def creation_script_tmp(self, output: str | Path, search_area=5) -> Path:
        """this method creates a temporary script using a TCL script template and input data."""
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
        logging.debug(f'First point: {coordonnees.iloc[0]}')
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
            texte = texte.replace("FEED_ME_OUTPUT", str(output))
            script.write(texte)
        return tmp_script

    def process_results(self, output_path: str) -> pd.DataFrame:
        """docstring"""  # TODO
        meas_df = pd.read_csv(output_path, index_col=False, na_values="unknown")
        # TODO : rename in tcl file?
        meas_df.rename(columns={'Gauge ': "name", ' Layer ': "layer",
                                ' Polarity (polygon) ': "polygon_tone",
                                ' X_dimension(nm) ': "x_dim", ' Y_dimension(nm) ': "y_dim",
                                'pitch_x(nm)': "pitch_x", 'pitch_y(nm)': "pitch_y",
                                ' min_dimension(nm)': "min_dim",
                                ' complementary(nm)': "complement_min_dim",
                                ' pitch_of_min_dim(nm)': "pitch_min_dim"},
                       inplace=True)
        # Drop invalid rows
        # FIXME measure out of range? -> modify tcl to handle empty measurement
        meas_df.replace({'x_dim': {0: None}, 'y_dim': {0: None}}, inplace=True)
        meas_df.replace('Pitch non symetrical', '0', inplace=True)  # TODO better
        meas_df.replace({'polygon_tone': "CD"}, "LINE", inplace=True)
        meas_df.dropna(subset=["x_dim", "y_dim"], inplace=True)

        return meas_df

    def output_measurement_file(self, df, output_dir, recipe_name) -> None:
        """docstring"""  # TODO
        try:
            # output_measure_df = df[['name', 'x', 'y']].copy()
            # output_measure_df['magnification'] = json_conf["magnification"]
            measure_output_file = Path(f"{output_dir}/measure_{recipe_name}").with_suffix(".csv")
            df.to_csv(measure_output_file, index=False)
            if measure_output_file.exists():
                logger.info(f"Measurement file saved successfully at {measure_output_file}")
        except Exception as e:
            logger.error(f"An error occurred while saving the file: {e}")

    def run_measure(self, output_dir: Path = None, recipe_name: str = None) -> pd.DataFrame:
        """run_measure is a method that calls all the requirement from mesure."""
        self.apply_offset()
        measure_tempfile = tempfile.NamedTemporaryFile(
            dir=Path.home() / "tmp")
        # TODO where to store tmp files (script + results)

        tmp = self.creation_script_tmp(measure_tempfile.name)
        logger.info('2. measurement')
        lance_script(tmp, verbose=True)
        meas_df = self.process_results(measure_tempfile.name)
        parser_df = self.parser_df.copy()
        nm_per_unit = {'dbu': 1000/self.precision, 'nm': 1, 'um': 1000}
        parser_df[["x", "y"]] *= nm_per_unit[self.unit]
        try:
            parser_df[["x_ap", "y_ap"]] *= int(float(nm_per_unit[self.unit]))
        except ValueError:
            pass
        parser_df = parser_df.drop_duplicates(subset=['name'])
        merged_dfs = pd.merge(parser_df, meas_df, on="name")
        # TODO: cleanup columns in merged df
        # logger.debug(f"debug cleanup columns measure.py : {merged_dfs.columns.tolist()}")

        # DEBUG copy results CSV
        # results = Path(measure_tempfile_path).read_text()
        # (Path(__file__).parents[2]/"recipe_output"/"measure_output.csv").write_text(results)
        measure_tempfile.close()  # remove temporary script
        if output_dir and recipe_name is not None:
            self.output_measurement_file(merged_dfs, output_dir, recipe_name)
        if not merged_dfs.empty:
            logger.info('Measurement done')
        # logger.debug(merged_dfs.columns)
        return merged_dfs
