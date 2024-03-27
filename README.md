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
* parses a ssfile
* runs measure
* merges the informations between the first two
* calculates the last values to enter in the <EPS_Data> of the recipe
* generates a .csv and .json file

### inputs&outputs :
To use this software, you will need to enter the following informations :
* Genepy ssfile
* layout
* layer
* Input&output folders (storing)

This software will return :
* a SEM recipe in .hss or .csv format (matching the Hitachi requirements)
* some documentation
* some template in .json format (that should be stored in a DB in order to reuse the created recipe afterwards)

## Installation :
Make sure you have the correct environnement first  
Create a folder on your local machine (Unix) : 
```bash
cd <your_folder_name>
```
Clone from the folder repository
```bash
git clone ssh://gitolite@codex.cro.st.com/retdev/semrc.git
```
Download the libraries used in the app
```bash
pip install -r requirements.txt
```
Then run main.py with the following command
```bash
python __main__.py
```
Enjoy your free time ! SEMRC is cooking a recipe for you !

### Tree structure :
```
semrc - project root
├── app
│   ├── app_checkers
│   │   └── user_input_checker.py
│   ├── connection_modules
│   │   ├── connection.py
│   │   └── shell_commands.py
│   ├── frontend
│   │   ├── __init__.py
│   │   └── main_front.py
│   ├── hss_modules
│   │   ├── dataframe_to_eps_data.py
│   │   ├── hss_creator.py
│   │   ├── hss_modificator.py
│   │   ├── __init__.py
│   │   └── template_to_all_sections.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── measure_modules
│   │   ├── measure.py
│   │   └── measure.tcl
│   ├── parser_modules
│   │   ├── csv_parser.py
│   │   ├── excel_parser.py
│   │   ├── __init__.py
│   │   ├── parse.py
│   │   ├── ssfile_parser.py
│   └── └── xml_parser.py
├── assets
│   └── template_SEM_recipe.json
├── .git
├── .gitignore
├── README.md
├── recipe_output
│   ├── recipe.csv
│   └── recipe.json
├── requirements.txt
├── .temp
├── tests
│   ├── __init__.py
│   ├── test_connection_modules
│   │   ├── __init__.py
│   │   └── test_shell_commands.py
│   ├── test_hss_modules
│   │   ├── __init__.py
│   │   ├── test_df_to_eps_data.py
│   │   ├── test_hss_creator.py
│   │   ├── test_template_to_all_sections.py
│   │   └── test_temp_output.hss
│   ├── test_measure.py
│   └── test_parser_modules
│       └── test_ssfile_parser.py
```

### Modules :
Here is a list of all the modules used in this app :
* python - Version 3.10.4  
* numpy - Version 1.23.0
* pandas - Version 1.4.3
<!-- * re - Version ? 2022.4.24 -->
<!-- * pathlib - Version ? -->
<!-- * subprocess - Version ? -->

#### Developers :
* Romain Chaneliere - DevOps apprentice @STMicroelectronics
* Romain Bange - PhD @STMicroelectronics

#### Legal :
This software is intended for use by the STMicroelectronics' RET/OPC team at Crolles & Rousset and should only be used as part of this organization. Any use of this software outside of this organization is strictly prohibited.

<!-- STMicroelectronics assumes no liability for any damages resulting from the use of this software outside of its intended purpose. -->