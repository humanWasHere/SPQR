# SPQR project
SEM Professional Quick Recipe - software for OPC applications

## Table of matters
0. [Quick start](#quick-start)
1. [General informations](#spqr's-purpose-)
2. [Features](#features-)
3. [Inputs & outputs](#inputs&outputs-)
4. [Installation](#installation-)
5. [Tree structure](#tree-structure-)
6. [Modules](#modules-)
7. [Developers](#developers-)
8. [Legal](#legal-)

## Quick start
Command to launch the deployed app : 
```bash
/work/retprod/src/deploy/semrc/build --help
```

## SPQR's purpose :
The SPQR project finds its root in a highly qualified team which is the RET team.
This project is led by Romain Bange and developed by Romain Chaneliere.

It is meant to automatically make SEM recipes in order to ease user interactions with Recipe Director.

### Features :
At the moment, this tool processes the following actions :  
* gets coordinates sources (by parsing a different coordinate sources)
* runs measure  
* calculates and define the sections and values of the recipe  
* generates a .csv and .json file  
* exports .csv recipe and layout on QCG 5k is needed  

### inputs&outputs :
To use this software, you will need to enter the following informations :
* Coordinate source (like Genepy ssfile, calibre rulers or first coordinates of an OPCField matrix)
* layout
* layer(s) (at least the main layer of interest)
* magnification
* MP_Template (prefered)
* Step (post litho or post etch)

This software will :
* return a SEM recipe in .csv format (matching the Hitachi requirements)
* return a SEM recipe in .json format (in order to be reused later)
* export the .csv recipe and the layout on the QCG5k (if specified)
<!-- * some documentation (made with sphinx) -->
<!-- * some template in .json format (that should be stored in a DB in order to reuse the created recipe afterwards) -->

## Installation :
Move to a directory in which you want the project to be stored : 
```bash
cd <your_folder_name>
```
Make sure you have a SSH key exchange to codex. Else, follow the documentation below :  
```
https://stmicroelectronics.sharepoint.com/:w:/r/sites/RETCROLLES/Projects%20development/SEM%20Recipe%20Creator/doc/SPQR%27s_user_documentation.docx?d=wd4248d7530144c1d8102960288b790c6&csf=1&web=1&e=UBjYLU
```
Clone from the folder repository
```bash
git clone ssh://gitolite@codex.cro.st.com/retdev/semrc.git
```
Change folder to access content of the app  
```
cd spqr
```
Download the libraries used in the app
```bash
pip install -r requirements.txt
```
Then run __main__.py with the following command (runs as package)  
```bash
python -m app
```
Enjoy your free time ! SPQR is cooking a recipe for you !

### Tree structure :
```
spqr - project root
├── app
│   ├── data_structure.py
│   ├── .env
│   ├── export_hitachi
│   │   ├── eps_data.py
│   │   ├── hss_creator.py
│   │   ├── hss_editor.py
│   │   ├── __init__.py
│   │   └── section_maker.py
│   ├── __init__.py
│   ├── interfaces
│   │   ├── calibre_python.py
│   │   ├── __init__.py
│   │   ├── input_checker.py
│   │   ├── mask_db.py
│   │   └── recipedirector.py
│   ├── __main__.py
│   ├── measure
│   │   ├── __init__.py
│   │   ├── measure.py
│   │   ├── measure.tcl
│   ├── parsers
│   │   ├── csv_parser.py
│   │   ├── file_parser.py
│   │   ├── __init__.py
│   │   ├── json_parser.py
│   │   ├── parse.py
│   │   ├── ssfile_parser.py
│   │   ├── tacx_parser.py
│   │   └── xml_parser.py
│   └── setup.py
├── assets
│   ├── app_config.json
│   └── template_SEM_recipe.json
├── ci_pipeline.csh
├── .coverage
├── .flake8
├── .git
│   └── ...
├── .gitignore
├── htmlcov
│   └── coverage_lib...
├── integration
│   ├── __init__.py
│   └── test_integration.py
├── poetry.lock
├── pyproject.toml
├── README.md
├── recipe_output
│   ├── recipes_outputed...
│   └── test_env
│       └── test_env_recipes_outputed...
├── requirements.txt
├── sourceme.csh
├── sphinx
│   └── auto_doc_lib...
└── tests
    ├── __init__.py
    ├── test_export_hitachi
    │   ├── __init__.py
    │   ├── test_eps_data.py
    │   ├── test_hss_creator.py
    │   └── test_section_maker.py
    ├── testfiles
    │   ├── COMPLETED_TEMPLATE.gds
    │   ├── .COMPLETED_TEMPLATE.gds.20240506-172141.pyratImplementation.GTCheck
    │   ├── ssfile_proto.txt
    │   └── test_template.json
    ├── test_measure.py
    ├── test_output
    │   └── recipe.json
    ├── test_parsers
    │   ├── test_json_parser.py
    │   ├── test_parse.py
    │   ├── test_ssfile_parser.py
    │   └── test_xml_parser.py
    └── tmp
```

### Modules :
Here is a list of the main modules used in this app :
* python - Version 3.10.4  
* numpy - Version 1.23.0
* pandas - Version 1.4.3
<!-- * re - Version ? 2022.4.24 -->
<!-- * pathlib - Version ? -->
<!-- * subprocess - Version ? -->

### Developers :
* Romain Chaneliere - DevOps apprentice @STMicroelectronics
* Romain Bange - PhD @STMicroelectronics

### Legal :
This software is intended for use by the STMicroelectronics' RET/OPC team at Crolles & Rousset and should only be used as part of this organization. Any use of this software outside of this organization is strictly prohibited.

<!-- STMicroelectronics assumes no liability for any damages resulting from the use of this software outside of its intended purpose. -->