# import tempfile
import subprocess
import pandas as pd
from pathlib import Path
# from pyrat.DesignControler import DesignControler
# from pyratImplementation.GTCheck.GTCheckService import GTcheckError


class measure:
    def __init__(self, df_file):
        self.INPUT_DF = df_file

    def creation_script_tmp(coords: pd.DataFrame, layout, layers, output, search_area=5, unit="nm"):
        tcl_template = Path(__file__).parent / "measure.tcl"
        # Place temporary script in user's home because /tmp is not shared across farm
        tmp_script = Path.home() / "tmp" / "Script_tmp.tcl"
        # tmp_script = tempfile.NamedTemporaryFile(suffix=".tcl", dir=Path.home()/"tmp")  # gets deleted out of scope?

        precision = measure.layout_peek(layout, "precision")
        # precision = DesignControler(layout).getPrecisionNumber()  # raises GTcheckError
        correction = {'um': 1, 'nm': 1000, 'dbu': precision}
        # Format coordinates as [{name x y}, ...]
        coordonnees = [f"{{{' '.join(row.astype(str).tolist())}}}" for _, row in coords.iterrows()]

        with open(tcl_template, "r", encoding="utf-8") as template, open(tmp_script, "w") as script:
            texte = template.read()
            texte = texte.replace("FEED_ME_LAYER", ' '.join(layers))
            texte = texte.replace("FEED_ME_SEARCH_AREA", str(search_area))
            texte = texte.replace("FEED_ME_PRECISION", precision)
            texte = texte.replace("FEED_ME_CORRECTION", str(correction[unit]))
            texte = texte.replace("FEED_ME_COORDINATES", '\n'.join(coordonnees))
            texte = texte.replace("FEED_ME_GDS", layout)
            texte = texte.replace("FEED_ME_OUTPUT", output)
            script.write(texte)
        return tmp_script

    def find_host():
        # From /work/ratsoft/bin/fastlinux7
        cmd = 'use lib "/work/ratsoft/lib/perlmod"; use Rat::choose_host; use strict;' \
            'print &choose_host::best_machine( "lx24-amd64", "rh70", 100, 1, 0, "all.q" );'
        choose_host = subprocess.run(f"perl -e '{cmd}'", shell=True, stdout=subprocess.PIPE)
        host = choose_host.stdout.decode()
        return host

    def layout_peek(layout, *options):
        options = ['-'+opt if not opt.startswith('-') else opt for opt in options]  # add dash if needed
        # assert set(options).issubset({"-precision", "-topcell", "-layers", "-bbox"})
        host = measure.find_host()
        peek_cmd = f"setcalibre rec >/dev/null; calibredrv -a puts [layout peek {layout} {' '.join(options)}]"
        peek = subprocess.run(["ssh", host, peek_cmd], stdout=subprocess.PIPE, text=True)
        return peek.stdout.splitlines()[-1].strip()

    def lance_script(script, debug="/dev/null", verbose=True):
        # cmd = f"setcalibre rec >/dev/null; calibredrv -64 {script} | tee {debug}"  # 2.71 s ± 43.6 ms
        host = measure.find_host()
        # todo: pexpect?
        cmd = "setenv MGC_HOME /sw/mentor/calibre/2018.4_34.26/aoi_cal_2018.4_34.26; " \
            "setenv PATH $MGC_HOME/bin:$PATH; " \
            "setenv MGLS_LICENSE_FILE 1717@cr2sx03400:1717@cr2sx03401:1717@cr2sx03402; " \
            "calibredrv -64 {} | tee {}".format(script, debug)  # 2.2 s ± 48.9 ms
        process = subprocess.Popen(["ssh", host, cmd], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
        if verbose:
            for line in process.stdout:  # .readlines()  # TODO: tqdm
                print(line.strip())
        outs, errs = process.communicate()
        if errs:
            raise ChildProcessError(errs)
        return host

    def sequence_auto(coords, layout, layers):  # username=user_name
        # results = tempfile.NamedTemporaryFile(dir=Path("/")/f"work/opc/all/users/{username}/semrc/.temp/")
        results = "/work/opc/all/users/chanelir/semrc-outputs/measure.temp"
        tmp = measure.creation_script_tmp(coords, layout, layers, results, unit="dbu")
        measure.lance_script(tmp, verbose=True)
        meas_df = pd.read_csv(results, index_col=False)
        # results.close()  # remove temporary script
        return meas_df

    def clean_unknown(dataframe):
        if dataframe.isin(['unknown']).any().any():
            new_dataframe = dataframe.copy()
            new_dataframe = new_dataframe[new_dataframe != 'unknown'].dropna()
            return new_dataframe
        else:
            return dataframe
