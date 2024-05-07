"""
Interface with DesignGauge station
"""
import os
from pathlib import Path
import pexpect
import socket

from dotenv import load_dotenv
import lxml.etree


try:
    DG_HOST = socket.gethostbyname("c2x20007.cr2.st.com")
except socket.gaierror:
    # c2x20007.cr2.st.com could not be resolved from compute farm
    DG_HOST = "10.18.125.204"
DG_TEMLATES = f"upguest@{DG_HOST}:/Designgauge/Template/"  # Templates
# f"upguest@{DG_HOST}:/Designgauge/Template/AMP/"  # MP templates
DG_CSVUP = f"upguest@{DG_HOST}:/DGTransferData/DGUpload/"  # upload CSV
DG_CSVDOWN = f"downguest@{DG_HOST}:/DGTransferData/DGDownload/"  # download CSV
DG_DESIGNDATA = f"ddguest@{DG_HOST}:/design_data/data/"  # upload GDS
DG_RECIPE = "/Designgauge/DGData/{techno}/Library/{maskset}/{recipe}"\
    .format(techno="OPC_C028", maskset="2822A", recipe="SJ71_NOSO_2822A_scanmatch_9fields")
# design_data = lxml.etree.parse(f{DG_RECIPE}/IDD.xml").find("IDD/DesignDataName").text
# ex: GS2_C028_NOSO_2822A_OPCfield
# f"{DG_DESIGNDATA}/{design_data}.gds"


# TODO change to dotenv ?
def get_pw(dest):
    import json
    login = dest.split('@')[0]
    # load_dotenv()
    # secrets = os.getenv(dest)
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
    child = pexpect.spawn(
        f"ssh upguest@{DG_HOST} cat /Designgauge/Template/{template_type}/{name}.xml")
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
