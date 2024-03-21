import tempfile
import subprocess
import pandas as pd
from pathlib import Path
# from pyrat.DesignControler import DesignControler
# from pyratImplementation.GTCheck.GTCheckService import GTcheckError

# TODO change path access if code is running on prod serv
# does it closes the temp file ?
# Warning Path must be str not Path file


class Measure:
    def __init__(self, parser_input: pd.DataFrame, layout, layers: list, tcl_measure_file=None):
        if tcl_measure_file is None:
            self.tcl_script = Path(__file__).parent / "measure.tcl"
            if not self.tcl_script.exists():
                raise FileNotFoundError(f"Could not find {self.tcl_script}")
        self.parser_df = parser_input
        self.x_y_points = parser_input[['name', 'x', 'y']]
        self.layout = layout
        self.layers = layers
        # if isinstance(layers, list):
        #     self.layers = layers
        # else:
        #     try:
        #         self.layers = [layers]
        #     except (TypeError):
        #         raise TypeError("layers argument must be a list")

    def find_host(self) -> str:
        '''uses perl script to find best available machine to execute a task'''
        # From /work/ratsoft/bin/fastlinux7
        cmd = 'use lib "/work/ratsoft/lib/perlmod"; use Rat::choose_host; use strict;' \
            'print &choose_host::best_machine( "lx24-amd64", "rh70", 100, 1, 0, "all.q" );'
        try:
            choose_host = subprocess.run(
                ['perl', '-e', cmd], stdout=subprocess.PIPE, check=True)
            host = choose_host.stdout.decode()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run Perl script: {e}") from e
        return host

    def layout_peek(self, *options) -> bytes:
        '''runs command "layout peek" in Calibre, in ssh, on a defined machine by find_host() in order to extract result'''
        options = [
            '-'+opt if not opt.startswith('-') else opt for opt in options]  # add dash if needed
        # assert set(options).issubset({"-precision", "-topcell", "-layers", "-bbox"})
        host = self.find_host()
        peek_cmd = f"setcalibre rec >/dev/null; calibredrv -a puts [layout peek {self.layout} {' '.join(options)}]"
        peek = subprocess.run(["ssh", host, peek_cmd],
                              stdout=subprocess.PIPE, text=True)
        return peek.stdout.splitlines()[-1].strip()

    def creation_script_tmp(self, output, search_area=5, unit="nm") -> Path:
        '''this method creates a temporary script using a TCL script template and input data'''
        # TODO this method should close temp file ?
        # TODO rationnaliser l'emplacement des fichiers temporaires
        # Place temporary script in user's home because /tmp is not shared across farm
        tmp_script = Path.home() / "tmp" / "Script_tmp.tcl"
        # tmp_script = tempfile.NamedTemporaryFile(suffix=".tcl", dir=Path.home()/"tmp")  # gets deleted out of scope?

        precision = self.layout_peek("precision")
        # precision = DesignControler(layout).getPrecisionNumber()  # raises GTcheckError
        correction = {'um': 1, 'nm': 1000, 'dbu': precision}
        # Format coordinates as [{name x y}, ...]
        coordonnees = [
            f"{{{' '.join(row.astype(str).tolist())}}}" for _, row in self.x_y_points.iterrows()]

        with open(self.tcl_script, "r", encoding="utf-8") as template, open(tmp_script, "w") as script:
            texte = template.read()
            texte = texte.replace("FEED_ME_LAYER", ' '.join(self.layers))
            texte = texte.replace("FEED_ME_SEARCH_AREA", str(search_area))
            texte = texte.replace("FEED_ME_PRECISION", precision)
            texte = texte.replace("FEED_ME_CORRECTION", str(correction[unit]))
            texte = texte.replace("FEED_ME_COORDINATES",
                                  '\n'.join(coordonnees))
            texte = texte.replace("FEED_ME_GDS", self.layout)
            texte = texte.replace("FEED_ME_OUTPUT", output)
            script.write(texte)
        return tmp_script

    def lance_script(self, script, debug="/dev/null", verbose=True) -> str:
        '''runs Calibre script by using "calibredrv"'''
        # cmd = f"setcalibre rec >/dev/null; calibredrv -64 {script} | tee {debug}"  # 2.71 s ± 43.6 ms
        host = self.find_host()
        # TODO : pexpect?
        # TODO maintenabilité + portée grenoble
        cmd = "setenv MGC_HOME /sw/mentor/calibre/2018.4_34.26/aoi_cal_2018.4_34.26; " \
            "setenv PATH $MGC_HOME/bin:$PATH; " \
            "setenv MGLS_LICENSE_FILE 1717@cr2sx03400:1717@cr2sx03401:1717@cr2sx03402; " \
            "calibredrv -64 {} | tee {}".format(script,
                                                debug)  # 2.2 s ± 48.9 ms
        process = subprocess.Popen(["ssh", host, cmd], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
        if verbose:
            for line in process.stdout:  # .readlines()  # TODO: tqdm
                print(line.strip())
        outs, errs = process.communicate()
        if errs:
            raise ChildProcessError(errs)
        return host

    def process_results(self, output_path) -> pd.DataFrame:
        meas_df = pd.read_csv(output_path, index_col=False, na_values="unknown")
        # TODO : traiter les "Pitch non symetrical" -> minimum?
        meas_df.dropna(subset=[" X_dimension(nm) ", " Y_dimension(nm) "], inplace=True)  # invalid rows
        # TODO : rename in tcl file?
        meas_df.rename(columns={'Gauge ': "name", ' X_dimension(nm) ': "x_dim", ' Y_dimension(nm) ': "y_dim",
                                'pitch_x(nm)': "pitch_x", 'pitch_y(nm)': "pitch_y", ' Polarity (polygon) ': "polarity"},
                       inplace=True)
        # TODO orientation, min_dimension...
        return meas_df

    def run_measure(self) -> pd.DataFrame:
        '''runs Calibre script to automatically measure a layout'''
        measure_tempfile = tempfile.NamedTemporaryFile(dir=Path(__file__).resolve().parents[2] / ".temp")
        # TODO where to store tmp files (script + results)
        measure_tempfile_path = measure_tempfile.name
        tmp = self.creation_script_tmp(measure_tempfile_path, unit="dbu")
        self.lance_script(tmp, verbose=True)
        meas_df = self.process_results(measure_tempfile_path)

        merged_dfs = pd.merge(self.parser_df, meas_df, on="name")

        measure_tempfile.close()

        return merged_dfs
