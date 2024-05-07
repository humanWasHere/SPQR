import subprocess

from pyter.calibre import DesignControlerRet


# TODO migration -> layout_peek ou MOA's library


def find_host() -> str:
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


def layout_peek(layout, *options) -> bytes:
    '''runs command "layout peek" in Calibre, in ssh, on a defined machine by find_host() in order to extract result'''
    options = ['-'+opt if not opt.startswith('-') else opt for opt in options]  # add dash if needed
    # assert set(options).issubset({"-precision", "-topcell", "-layers", "-bbox"})
    host = find_host()
    peek_cmd = f"setcalibre rec >/dev/null; calibredrv -a puts [layout peek {layout} {' '.join(options)}]"
    peek = subprocess.run(["ssh", host, peek_cmd], stdout=subprocess.PIPE, text=True)
    return peek.stdout.splitlines()[-1].strip()


def get_precision_from_layout(layout: str):
    design = DesignControlerRet(str(layout))
    result = design.getPrecisionNumber()
    return int(float(result))


def get_topcell_from_layout(layout):
    design = DesignControlerRet(str(layout))
    result = design.getTopcellNameString()
    return str(result)


def lance_script(script, debug="/dev/null", verbose=True) -> str:
    '''runs Calibre script by using "calibredrv"'''
    # cmd = f"setcalibre rec >/dev/null; calibredrv -64 {script} | tee {debug}"  # 2.71 s ± 43.6 ms
    host = find_host()
    # TODO : pexpect?
    # TODO maintenabilité + portée grenoble
    cmd = "setenv MGC_HOME /sw/mentor/calibre/2018.4_34.26/aoi_cal_2018.4_34.26; " \
        "setenv PATH $MGC_HOME/bin:$PATH; " \
        "setenv MGLS_LICENSE_FILE 1717@cr2sx03400:1717@cr2sx03401:1717@cr2sx03402; " \
        "calibredrv -64 {} | tee {}".format(script,
                                            debug)  # 2.2 s ± 48.9 ms
    process = subprocess.Popen(["ssh", host, cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               bufsize=1, text=True)
    if verbose:
        for line in process.stdout:  # .readlines()  # TODO: tqdm
            print(line.strip())
    outs, errs = process.communicate()
    if errs:
        raise ChildProcessError(errs)
    return host
