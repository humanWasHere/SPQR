# SEMRC project
SEM Professional Quick Recipe - software for OPC applications

## Table of matters
1. [General informations](#semrc's-purpose-)
2. [Features](#features-)
3. [Inputs & outputs](#inputs&outputs-)
4. [Installation](#installation-)
5. [Tree structure](#tree-structure-)
6. [Modules](#modules-)
7. [Developers](#developers-)
8. [Legal](#legal-)

## SEMRC's purpose :
The SEMRC project finds its root in a highly qualified team which is the RET team.
This project is led by Romain Bange and developed by Romain Chaneliere.

It is meant to automatically make SEM recipes in order to ease user interactions with Recipe Director.

### Features :
At the moment, this tool processes the following actions :  
* gets coordinates sources (by parsing a ssfile or getting first coordinate in a matrix)
* runs measure
* calculates and define the sections and values of the recipe  
* generates a .csv and .json file  
* exports data on QCG 5k

### inputs&outputs :
To use this software, you will need to enter the following informations :
* Coordinate source (like Genepy ssfile, calibre rulers or first coordinates of an OPCField matrix)
* layout
* layer(s) (at least the main layer of interest)
* mag
* MP_Template
* Step (post litho ou post etch)

This software will :
* return a SEM recipe in .csv format (matching the Hitachi requirements)
* return a SEM recipe in .json format (in order to be reused later)
* export the .csv recipe on the QCG5k (if specified)
<!-- * some documentation (made with sphinx) -->
<!-- * some template in .json format (that should be stored in a DB in order to reuse the created recipe afterwards) -->

## Installation :
Create a folder on your local machine (Unix) : 
```bash
cd <your_folder_name>
```
Clone from the folder repository
```bash
git clone ssh://gitolite@codex.cro.st.com/retdev/semrc.git
```
Change folder to access content of the app  
```
cd semrc
```
Download the libraries used in the app
```bash
pip install -r requirements.txt
```
Then run __main__.py with the following command (runs as package)  
```bash
python -m app
```
Enjoy your free time ! SEMRC is cooking a recipe for you !

### Tree structure :
```
semrc - project root
├── app
│   ├── data_structure.py
│   ├── .env
│   ├── export_hitachi
│   │   ├── eps_data.py
│   │   ├── hss_creator.py
│   │   ├── hss_editor.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── section_maker.py
│   ├── __init__.py
│   ├── interfaces
│   │   ├── calibre_python.py
│   │   ├── __init__.py
│   │   ├── input_checker.py
│   │   ├── mask_db.py
│   │   ├── __pycache__
│   │   └── recipedirector.py
│   ├── __main__.py
│   ├── measure
│   │   ├── measure.py
│   │   ├── measure.tcl
│   │   └── __pycache__
│   └── parsers
│       ├── csv_parser.py
│       ├── __init__.py
│       ├── json_parser.py
│       ├── parse.py
│       ├── __pycache__
│       ├── ssfile_parser.py
│       └── xml_parser.py
├── assets
│   └── template_SEM_recipe.json
├── ci_pipeline.csh
├── .coverage
├── .coveragerc
├── .flake8
├── .git
├── .gitignore
├── htmlcov
├── pytest.ini
├── README.md
├── requirements.txt
└── tests
    ├── __init__.py
    ├── test_export_hitachi
    │   ├── __init__.py
    │   ├── test_eps_data.py
    │   ├── test_hss_creator.py
    │   └── test_section_maker.py
    ├── testfiles
    │   ├── COMPLETED_TEMPLATE.gds
    │   ├── ssfile_proto.txt
    │   └── test_template.json
    ├── test_measure.py
    ├── test_output
    │   └── recipe.json
    └── test_parsers
        ├── test_ssfile_parser.py
        └── test_xml_parser.py
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