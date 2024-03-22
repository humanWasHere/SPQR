# FIXME file unused
# FIXME variables in file unused
# !/sw/freetools/python_anaconda/2021.11/rh70_64/bin/python3.9
"""
Connection interfaces with RetDB, DesignGauge station upload/download, and Sharepoint Online
"""
import os
import socket
import pexpect
import requests
import numpy as np
import pandas as pd
import lxml.etree
import xml.etree.ElementTree as et
from pathlib import Path
from sqlalchemy.engine import create_engine
try:
    import cx_Oracle
except ModuleNotFoundError:
    # not installed in python_anaconda > 2020.02
    import sys
    sys.path.append("/sw/freetools/python_anaconda/5.2.0/rh70_64/lib/python3.6/site-packages/"
                    "cx_Oracle-7.2.1-py3.6-linux-x86_64.egg")  # client version 11.2.0.3.0 - same as cx_Oracle 8.3.0 from python3.10
    import cx_Oracle

RETDB = {
    'user': "retadm",
    'password': "",
    'dsn': "c2x3028.cr2.st.com:1529/ret"
}
ENGINE = create_engine(f"oracle+cx_oracle://{RETDB['user']}:{RETDB['password']}@{RETDB['dsn']}")
# Useful queries
USERS_QUERY = "SELECT * FROM all_users"


# Interface with RetDB
def fast_query(query):
    with cx_Oracle.connect(**RETDB) as con:
        cur = con.cursor()
        cur.execute(query)
        results = cur.fetchall()
        # column_names = [row[0] for row in cur.description]
    return results


def get_mask_info(maskset):
    queries = ["SELECT * FROM WAFER WHERE MASK_NAME= :mask",
               "SELECT * FROM FRAME_MASK WHERE FRAME_NAME= :mask",  # retdbLib.recup_infos_masket -> infos_maskset_glob
               "SELECT * FROM BLOCK WHERE MASK_NAME= :mask ORDER BY BLOCK_NAME,BLOCK_NAME_I ASC",  # block info
               "SELECT * FROM BLOCK WHERE MASK_NAME= :mask AND BLOCK_NAME LIKE 'F%' ORDER BY BLOCK_NAME ASC",
               "SELECT * FROM GDS_INFO WHERE MASKSET= :mask AND DEVICE LIKE 'P%'",
               "SELECT MAX(BLOCK_NAME_I) FROM BLOCK WHERE MASK_NAME= :mask"]
    # with cx_Oracle.connect(**RETDB) as con:
    for query in queries:
        yield pd.read_sql(query, ENGINE, params={'mask': maskset})


def get_block_info(maskset):
    # From /work/retprod/src/RETToolsBox/Modules/RET/ConvertXY/last/ConvertXY.tcl:172
    # query = "SELECT * FROM BLOCK WHERE MASK_NAME= :mask ORDER BY BLOCK_NAME,BLOCK_NAME_I ASC"
    query = "SELECT * FROM BLOCK WHERE MASK_NAME= :mask ORDER BY BLOCK_NAME,BLOCK_NAME_I ASC"
    # with cx_Oracle.connect(**RETDB) as con:
    df = pd.read_sql(query, ENGINE, params={'mask': maskset})
    return df


mask_info = list(get_mask_info("282YA"))


def read_mrg(path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=' ', names=["tx", "ty", "r"])
    df.index = df.index.str.rsplit('.').str[0].str.split('_').str[-1]
    df.index = df.index.str.replace("frame", "FR")
    return df


def translation(maskset):
    mask = list(get_mask_info(maskset))
    mask[2]['device'] = mask[2].block_name.str.split('-').str[0]
    frame = mask[1].squeeze()
    field = mask[2].iloc[1:].set_index('device')
    block = mask[4].set_index('device')

    # TODO: add logic for SLR matrices
    if any(field[['block_col', 'block_raw']].stack() > 1):
        # raise TypeError("Matriced products are not supported yet")
        print("Matriced products are not supported yet. Looking for existing MRG")
        if Path(f"/prj/opc/all/users/banger/mrg/{maskset}.mrg").exists():
            mrg_path = f"/prj/opc/all/users/banger/mrg/{maskset}.mrg"
        else:
            mrg_path = input("Please provide path to MRG file:")
        return read_mrg(mrg_path)

    # Compute GDS -> SEM translation
    # Initialize result dataframe, "mrg" style
    df = pd.DataFrame({'tx': frame.fr_x/2 - frame.overlap_x/2, 'ty': frame.fr_y/2 - frame.overlap_y/2, 'r': 0}, index=['FR'])

    if block.empty:
        return df

    # Check rotation
    ratio_coord = (block.ymax - block.ymin) / (block.xmax - block.xmin)
    ratio_size = field.bl_y / field.bl_x
    rotated = np.allclose(ratio_coord, 1/ratio_size) and not np.allclose(ratio_coord, 1)
    # return  ratio_coord, ratio_size
    if maskset[:2] == "28" or rotated:  #TODO: robustize
        rotation = 90
    else:
        rotation = 0

    if rotation == 0:
        Tx = frame.fr_x/2 - frame.overlap_x/2 + field.center_x - (block.xmin + block.xmax)/2
        Ty = frame.fr_y/2 - frame.overlap_y/2 + field.center_y - (block.ymin + block.ymax)/2
    elif rotation == 90:
        Tx = frame.fr_x/2 - frame.overlap_x/2 + field.center_x + (block.ymin + block.ymax)/2
        Ty = frame.fr_y/2 - frame.overlap_y/2 + field.center_y - (block.xmin + block.xmax)/2
    return pd.concat([df, pd.DataFrame({'tx': Tx, 'ty': Ty, 'r': rotation})])


# Interface with DesignGauge station
# c2x20007.cr2.st.com cannot be resolved from compute farm  --> 10.18.125.204
try:
    DG_HOST = socket.gethostbyname("c2x20007.cr2.st.com")  # is this really necessary?
except socket.gaierror:
    DG_HOST = "10.18.125.204"
DG_TEMLATES = f"upguest@{DG_HOST}:/Designgauge/Template/"  # Templates
# f"upguest@{DG_HOST}:/Designgauge/Template/AMP/"  # MP templates
DG_CSVUP = f"upguest@{DG_HOST}:/DGTransferData/DGUpload/"  # upload CSV
DG_CSVDOWN = f"downguest@{DG_HOST}:/DGTransferData/DGDownload/"  # download CSV
DG_DESIGNDATA = f"ddguest@{DG_HOST}:/design_data/data/"  # upload GDS
DG_RECIPE = "/Designgauge/DGData/{techno}/Library/{maskset}/{recipe}"\
    .format(techno="OPC_C028", maskset="2822A", recipe="SJ71_NOSO_2822A_scanmatch_9fields")
# design_data = lxml.etree.parse(f{DG_RECIPE}/IDD.xml").find("IDD/DesignDataName").text  # GS2_C028_NOSO_2822A_OPCfield
# f"{DG_DESIGNDATA}/{design_data}.gds"


def get_pw(dest):
    import json
    login = dest.split('@')[0]
    secrets = json.loads((Path.home()/".secrets.json").read_text())
    return secrets[login]


def dg_transfer(source, destination, password=None):
    # Use rsync to copy with specific permissions
    if password is None:
        try:
            password = get_pw(destination)
        except FileNotFoundError:
            pass
    user = destination.split('@')[0] or source.split('@')[0]
    child = pexpect.spawn(f"rsync -v -t --perms --chmod=u+r,g+r,o+r {source} {destination}")
    child.expect("password:")
    child.sendline(password or input(f"{user}'s password: "))
    output = child.read().decode()  # todo: status check
    child.close()
    stdout = output.strip().replace('\r\n', '\n')
    return stdout or True


# TODO: raise exception if error (eg file not exist)
def upload_csv(file_path, password=None):
    _status = dg_transfer(file_path, DG_CSVUP, password)
    return _status


def upload_gds(file_path, password=None):
    _status = dg_transfer(file_path, DG_DESIGNDATA, password)
    return _status


def get_template(template_type, name, password=None, write_to=None):
    child = pexpect.spawn(f"ssh upguest@{DG_HOST} cat /Designgauge/Template/{template_type}/{name}.xml")
    child.expect("password:")
    child.sendline(password or input("upguest's password: "))
    xml = child.read().strip()
    child.close()
    template_tree = lxml.etree.fromstring(xml)
    # do some diffs ...
    if write_to is not None:
        if os.path.isfile(write_to):
            raise FileExistsError
        with open(write_to, 'w') as f:
            f.write(lxml.etree.tostring(template_tree, encoding="unicode", pretty_print=True))
    return template_tree


def strip_template_off(tree):
    tree_copy = tree.__copy__()
    for off in tree.findall(".//Off"):
        off.getparent().remove(off)
    return tree_copy


def sharepoint():
    # Interface with Sharepoint
    # https://sharepoint.stackexchange.com/questions/186740/using-linux-shell-scripting-to-upload-a-document-to-sharepoint
    # https://github.com/JonathanHolvey/sharepy
    os.environ['HTTPS_PROXY'] = "165.225.20.12:80"
    # Get user realm
    url = "https://login.microsoftonline.com/GetUserRealm.srf?login={}&xml=1"
    realm = et.fromstring(requests.get(url.format("romain.bange@st.com")).text)
    namespace = realm.find("NameSpaceType").text

    # API calls
    site = "https://stmicroelectronics.sharepoint.com/sites/RETCROLLES"
    list_url = f"{site}/_api/Web/Lists/GetByTitle('testList')/items"
    f"{site}/_api/web/GetFolderByServerRelativeUrl('RET%20Procedure%20%20Quality')?$expand=Folders,Files"

    cookies = {'FedAuth': "77u/PD9...",
               'rtFa': "OWMWpEM..."}
    # r = requests.post('http://wikipedia.org', cookies=cookies)


if __name__ == "__main__":
    print("cx_Oracle client version: ", cx_Oracle.clientversion())
    # with cx_Oracle.connect(**RETDB) as con:
    #     print("RetDB Oracle version:", con.version)
    maskset = "656YA"  # 6580A 657LA great testcases
    result = translation(maskset)
    print(result)
    # Check:
    # print(pd.read_csv(f"/prj/opc/all/users/banger/mrg/{maskset}.mrg", sep=' ', names=["block", "tx", "ty", "r"]))
    check_mrg = (
        pd.read_csv(f"/prj/opc/all/users/banger/mrg/{maskset}.mrg",
                sep=' ', names=["block", "tx", "ty", "r"]).set_index(result.index).drop(columns="block")
        == result
    )
    print(all(check_mrg))


def test():
    from connections import translation
    wd = "/work/opc/all/users/banger/custom/C065_GATE_matching/"
    df = translation("656YA")
    df.insert(0, 'layout', "crop_from_" + df.index + ".gds")
    df.to_csv("656YAgen.mrg", sep=' ', header=False, index=False)