# FIXME variables in file unused
"""
Interface with RetDB to fetch mask data
"""
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.engine import create_engine
try:
    import cx_Oracle
except ModuleNotFoundError:
    # not installed in python_anaconda > 2020.02
    import sys
    sys.path.append("/sw/freetools/python_anaconda/5.2.0/rh70_64/lib/python3.6/site-packages/"
                    "cx_Oracle-7.2.1-py3.6-linux-x86_64.egg") 
    # client version 11.2.0.3.0 - same as cx_Oracle 8.3.0 from python3.10
    import cx_Oracle

load_dotenv()

RETDB = {
    'user': "retadm",
    # 'password': dotenv["RET_DB_PASSWORD"],
    'password': os.getenv('RET_DB_PASSWORD'),
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


# if __name__ == "__main__":
#     print("cx_Oracle client version: ", cx_Oracle.clientversion())
#     # with cx_Oracle.connect(**RETDB) as con:
#     #     print("RetDB Oracle version:", con.version)
#     maskset = "656YA"  # 6580A 657LA great testcases
#     result = translation(maskset)
#     print(result)
#     # Check:
#     # print(pd.read_csv(f"/prj/opc/all/users/banger/mrg/{maskset}.mrg", sep=' ', names=["block", "tx", "ty", "r"]))
#     check_mrg = (
#         pd.read_csv(f"/prj/opc/all/users/banger/mrg/{maskset}.mrg",
#                 sep=' ', names=["block", "tx", "ty", "r"]).set_index(result.index).drop(columns="block")
#         == result
#     )
#     print(all(check_mrg))
