# Purpose
SEM Pro: Quick Recipe (SPQR) is meant to automate the generation of SEM recipes in order to ease RET user interactions with Recipe Director for OPC applications.

## Main features
At the moment, this tool performs the following actions:  
* parse a coordinate source file among a variety of supported types (see #Input),
* measure patterns in a layout at the intendend coordinates,
* calculate and define the sections and values of the recipe,
* generate an HSS recipe file (.csv) and JSON recipe file,
* export recipe and layout to Recipe Director.

# Quick start
Usage:
```
spqr build [-h] -c CONFIG [-r RECIPE] [-u] [-l RANGE [RANGE ...]] [-m]
```
Example command to generate a recipe:
```
spqr build -c ./my_config.json -r my_recipe1 --upload 
```

For a list of all available commands, run `spqr -h`
```
init                Generate default configuration files for quick start.
build               <<< Build a SEM recipe: main mode.
upload              Upload a given recipe and/or layout to Recipe Director.
test                Run the "testing" mode of the app. Meant for developers.
edit                Edit a given HSS recipe (experimental).
```
For detailed help on each command, run `spqr <command> -h`. For example: `spqr build --help`


# Input & output
To use this software, you will need to enter the following informations:
* Coordinate source (like Genepy ssfile, calibre rulers or first coordinates of an OPCField matrix)
* layout
* layer(s) (at least the main layer of interest)
* magnification
* MP_Template (prefered)
* Step (post litho or post etch)

This software will :
* return a SEM recipe in .csv format (HSS / Hitachi SpreadSheet)
* return a SEM recipe in .json format (in order to be reused later)
* export the .csv recipe and the layout to *Recipe Director* host (if `--upload` is specified)
<!-- * some documentation (made with sphinx) -->
<!-- * some template in .json format (that should be stored in a DB in order to reuse the created recipe afterwards) -->

# Installation (to rework)
Move to a directory in which you want the project to be stored : 
```bash
cd <your_folder_name>
```
Make sure you have a SSH key exchange to codex. Else, follow the [Word documentation](https://stmicroelectronics.sharepoint.com/:w:/r/sites/RETCROLLES/_layouts/15/Doc.aspx?sourcedoc=%7BD4248D75-3014-4C1D-8102-960288B790C6%7D&file=SPQR%27s_user_documentation.docx&action=view&mobileredirect=true&web=1) on RET Sharepoint Online.


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

## Tree structure
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
│   │   ├── cli.py
│   │   ├── __init__.py
│   │   ├── input_checker.py
│   │   ├── logger.py
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
│   │   └── xml_parser.py
│   ├── setup.py
│   └── web
│       ├── auth_app
│       ├── db.sqlite3
│       ├── home
│       ├── manage.py
│       ├── recipe_creation
│       └── spqr
├── assets
│   ├── init
│   │   ├── coordinate_file_ex.txt
│   │   └── user_config_ed.json
│   ├── app_config.json
│   └── template_SEM_recipe.json
├── ci_pipeline.csh
├── .coverage
├── .coveragerc
├── .flake8
├── .git
├── .gitignore
├── htmlcov
├── jenkinsfile
├── poetry.lock
├── pyproject.toml
├── README.md
├── recipe_output
├── requirements.txt
├── sourceme.csh
├── sphinx
├── spqr
├── spqr.log
├── tests
│   ├── end2end
│   │   └── test_e2e.py
│   ├── __init__.py
│   ├── integration
│   │   ├── __init__.py
│   │   └── test_integration.py
│   ├── testfiles
│   ├── tmp
│   └── unit
└── .venv
```

## Modules :
Here is a list of the main modules used in this app :
* python - Version 3.10.4  
* numpy - Version 1.23.0
* pandas - Version 1.4.3
<!-- * re - Version ? 2022.4.24 -->
<!-- * pathlib - Version ? -->
<!-- * subprocess - Version ? -->

# Developers :
* Romain Chaneliere - DevOps apprentice @STMicroelectronics
* Romain Bange - PhD @STMicroelectronics

# Legal :
This software is intended for use by the STMicroelectronics' RET/OPC team at Crolles & Rousset and should only be used as part of this organization. Any use of this software outside of this organization is strictly prohibited.

<!-- STMicroelectronics assumes no liability for any damages resulting from the use of this software outside of its intended purpose. -->