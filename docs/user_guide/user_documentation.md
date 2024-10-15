# SPQR - User’s documentation
SEM Pro: Quick Recipe v0.2.1  
Last update: 15/10/2024

## Table of matters
1. [What is SPQR?](#what-is-SPQR)  
    a. [Context and field of application](#context-and-field-of-application)  
    b. [Current advancement](#current-advancement)  
    c. [Tree structure of a recipe](#Tree-structure-of-a-recipe)  
2. [Quick start](#quick-start)  
    a. [Configuration file generation](#configuration-file-generation)  
    b. [Recipe generation](#recipe-generation)   
3. [Coordinate file sources](#coordinate-file-sources)  
4. [User configuration file](#user-configuration-file)  
    a. [Syntax and format](#syntax-and-format)  
    b. [Example of JSON configuration file](#example-of-JSON-configuration-file)  
    c. [User configuration file - Coordinate files](#user-configuration-file---Coordinate-files)  
    d. [User configuration file - OPCField](#user-configuration-file---OPCField)    
5. [Commands](#commands)  
    a. [Init](#init)  
    b. [Build](#build)  
    c. [Edit](#edit)  
    d. [Upload](#upload)  
    e. [Test](#test)  
6. [FAQ](#faq)  

## What is SPQR?

SEM Pro: Quick Recipe is meant to ease the process of CD-SEM recipe creation.

### Context and field of application

- **What is a SEM?** → A microscope
- **What is a SEM recipe?** → A file to execute instructions on a SEM
- **What is RCPD (Recipe Director)?** → A software to manage SEM recipe

SPQR takes different kinds of sources and is meant to need as minimum user interaction as possible. It produces a .csv file and a layout exported on Recipe Director.

### Current advancement

SPQR takes several types of coordinate sources for recipe creation:
- Genepy OPCField file (“ssfile”) → .csv
- OPCField matrix generation (no file)
- HSS file (recipe) → .csv
- Json file (recipe outputed from SPQR) → .json
- Calibre ruler file → .xml

These are part of the configuration file (.json) needed to create a recipe 

Its outputs:
- A HSS recipe → .csv
- A JSON recipe → .json
- (optional) a measurement file (saved as `measure_<your_recipe_name>`) → .csv

### Tree structure of a SPQR recipe

In order to have a better understanding of the structure of a recipe, we propose a tree structure to visualize more. These names correspond to flags or column names in which you can add different values.

The first 3 are constants which you should not modify (they only have one sublevel): `<FileID>`, `<Version>`, and `<Revision>`.

Here is the tree structure announced:

```bash
<CoordinateSystem>
    Type
    ACD_Type
<GPCoordinateSystem>
    Type
<Unit>
    Coordinate
    MP_Box
<GP_Data>
    GP_ID
    Type
    GP_X
    GP_Y
    GP_Template
    GP_Mag
    GP_Rot
    GP_Acceptance
<EPS_Data>
    EPS_ID, Type1, Move_X, Move_Y, Mode, EPS_Name, Ref_EPS_ID, EPS_Template, AP1_Template, AP2_Template, EP_Template, Type2, AP1_X, AP1_Y, AP1_Mag, AP1_Rot, Type3, AP1_AF_X, AP1_AF_Y, AP1_AF_Mag, Type4, AP1_AST_X, AP1_AST_Y, AP1_AST_Mag, Type5, AP2_X, AP2_Y, AP2_Mag, AP2_Rot, Type6, AP2_AF_X, AP2_AF_Y, AP2_AF_Mag, Type7, AP2_AST_X, AP2_AST_Y, AP2_AST_Mag, EP_Mag_X, EP_Mag_Y, EP_Rot, Type8, EP_AF_X, EP_AF_Y, EP_AF_Mag, Type9, EP_AST_X, EP_AST_Y, EP_AST_Mag, Type10, EP_ABCC_X, EP_ABCC_Y, Type11, MP1_X, MP1_Y, MP1_Template, MP1_PNo, MP1_DNo1, MP1_DNo2, MP1_Name, MP1_TargetCD, MP1_PosOffset, MP1_SA_In, MP1_SA_Out, MP1_MeaLeng, MP1_Direction, Type12, MP2_X, MP2_Y, MP2_Template, MP2_PNo, MP2_DNo1, MP2_DNo2, MP2_Name, MP2_TargetCD, MP2_PosOffset, MP2_SA_In, MP2_SA_Out, MP2_MeaLeng, MP2_Direction, Type13, MP3_X, MP3_Y, MP3_Template, MP3_PNo, MP3_DNo1, MP3_DNo2, MP3_Name, MP3_TargetCD, MP3_PosOffset, MP3_SA_In, MP3_SA_Out, MP3_MeaLeng, MP3_Direction, Type14, MP4_X, MP4_Y, MP4_Template, MP4_PNo, MP4_DNo1, MP4_DNo2, MP4_Name, MP4_TargetCD, MP4_PosOffset, MP4_SA_In, MP4_SA_Out, MP4_MeaLeng, MP4_Direction
<GPA_List>
    GPA_No
    Chip_X
    Chip_Y
    GP_ID
<GP_Offset>
    Offset_X
    Offset_Y
<EPA_List>
    EPA_No
    Chip_X
    Chip_Y
    EPS_ID
    Move_Mode
<IDD_Cond>
    DesignData
    CellName
    DCRot
    DCOffsetX
    DCOffsetY
    Tone
<IDD_Layer_Data>
    LayerNo
    DataType
    Type
    Level
    DUMMY
    Tone
    ColorNo
    FillNo
    LayerName 
<ImageEnv>
    Type
    Size
    CompressSW
    Quality
    MeasCur
    CrossCur
    AreaCur
    DDS
    MeasVal
    LinePro
    umMark
<Recipe>
    ClassName
    SEMCondNo
    WaferProperty
    SlotNum
    SlotNo1SW
    SlotNo2SW
    SlotNo3SW
    SlotNo4SW
    SlotNo5SW
    SlotNo6SW
    SlotNo7SW
    SlotNo8SW
    SlotNo9SW
    SlotNo10SW
    SlotNo11SW
    SlotNo12SW
    SlotNo13SW
    SlotNo14SW
    SlotNo15SW
    SlotNo16SW
    SlotNo17SW
    SlotNo18SW
    SlotNo19SW
    SlotNo20SW
    SlotNo21SW
    SlotNo22SW
    SlotNo23SW
    SlotNo24SW
    SlotNo25SW
    SlotNo26SW
    AutoCalibrationSW 
<MeasEnv_Exec>
    WA_ExecMode
    MA_ExecMode
    ME_ExecMode
    WA_ManualAssist
    MA_ManualAssist
    ME_ManualAssist
    WA_ImageSave
    MA_ImageSave
    ME_ImageSave
<MeasEnv_MeasRes>
    DiskSave
    SendToHost
    PrintOut
    NetTransfer
    Confirm
    Method
    LimitCheck
    hiFrame
```

## Quick start  

**What's needed to use SPQR**
- A configuration file in json following our internal structure and format
- A coordinate file (or OPCField case)

### Configuration file generation
Represented by the **`init`** command, generates either a generic configuration file for spqr, a coordinate file example or both. 
```bash
spqr init --help
```
```bash
usage: spqr init [-h] [-c CONFIG_FILE] [-x COORDINATE_FILE]

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Path (file or directory) to write a configuration file (JSON).
  -x COORDINATE_FILE, --coordinate_file COORDINATE_FILE
                        Path (file or directory) to write a generic coordinate file (genepy format).
```

Example of configuration file generation: 
```bash
spqr init -c -x
```

### Recipe generation
Represented by the **`build`** command, generates a recipe.

```bash
spqr build --help
```
```bash
usage: spqr build [-h] -c CONFIG [-r RECIPE] [-u] [-l RANGE [RANGE ...]] [-m]

Build a SEM recipe from a configuration file and coordinates. See `spqr init` command to get templates.

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to JSON configuration file containing the recipe parameters.
  -r RECIPE, --recipe RECIPE
                        Name of the recipe to run, from the JSON configuration file.
  -u, --upload_rcpd     Send HSS recipe (.csv) and layout to RecipeDirector machine.
  -l RANGE [RANGE ...], --line_select RANGE [RANGE ...]
                        Select range(s) of rows to include. Format: -l 50-60 150-160
  -m, --measure         Write the raw data measured from layout to recipe output directory
```

Example of build command usage
```bash
spqr build -c ./my_config.json -r my_recipe1 --upload -m
```

## Coordinate file sources 
1) OPCField matrix generation (OPCField Reverse)  
Actually not a coordinate file, you will need to input information about your OPCField in the [configuration file section](#user-configuration-file)

2) Genepy OPCField file / "SSfile"  
Currently, only OPCfield field generated by Genepy or manually created ssfile (matching the Genepy format) are supported by the application. Please, conform to this format. **With tabulation and .csv extension.**  
You should, at least, have these columns name: `Name`, `X_coord_Pat`, `Y_coord_Pat`, `X_coord_Addr`, `Y_coord_Addr`.  
`UNIT_COORD` column is optional and defaults to `nm`. 

3) Calibre rulers  
Calibre ruler files are fully supported. You can select points manually in Calibre using the option "allow multiple rulers" and the “ruler palette” and export them in an XML file. The center of the rulers will be used for pattern coordinate, and the ruler comment for pattern name (more documentation coming soon).  

> **_NOTE:_**
Calibre rulers with or without `<comment>` section is supported (corresponds to the name of the ruler).

4) HSS file (.csv)  
These are recipes that are meant to be reused as input for a new recipe.  
Existing recipes can be parsed.
<!-- Currently, only coordinate information is used (EPS_Data section).  -->

5) JSON recipe  
Json recipes are also existing recipes meant to be input for a new recipe.  
These JSON recipes should come from SPQR output since they should match our internal structure.  
<!-- Currently, only coordinate information is used (EPS_Data section).  -->

## User configuration file

This part is meant to explain the different possibilities of setting up a user config file in json. We have two main case flow. The case where a list of `coordinate source` is provided and the case of an `OPCField` (where coordinate matrix will be recreated). 

> **_NOTE:_**
You can have parameters for several recipes in this file since we launch the recipe according to the global key (flag).

### Syntax and format  
We advise users to use an IDE or any text editor which will check about the validity of the json. Also, you can first check about the validity of your JSON with online tools like: https://jsonformatter.curiousconcept.com/ .  

You file must :
- always match JSON format.
- use empty values must be noted as `“”` (double quotation marks).  
- use `dots` for floating values and commas are data separators.
- write all your coordinate and measurement values in `um`.

### Example of JSON configuration file

```json
{ 

    "opcfield_reverse": { 

        "recipe_name": "banger-X901A-GATE-etchbias", 

        "output_dir": "recipe_output/", 

        "coord_file": "", 

        "layout": "/work/opc/all/users/banger/X90M/GATE/HERMES_MPW/X901A_FR_TOPRIGHT_ALL_cropped_for_SEM.oas", 

        "layers": ["0.400"], 

        "ap1_template": "OPC_AP1_template_45K", 

        "ap1_offset": [0.35, -4.4], 

        "ap1_mag": 45000, 

        "ep_template": "", 

        "eps_template": "", 

        "magnification": 200000, 

        "mp_template": "X90M_GATE_PH", 

        "step": ["PH", "ET"], 

        "origin_x_y": [6216.487,29885.021], 

        "step_x_y": [6, 8.4], 

        "n_cols_rows": [4, 12] 

    }, 

    "coordinate_file": { 

        "recipe_name": "banger_X901A", 

        "output_dir": "recipe_output/", 

        "coord_file": "/work/opc/all/users/banger/X90M/GATE/HERMES_MPW/SJ71_X901A_GATE_OPCVERIF_FEM_PH2.csv", 

        "layout": "/work/opc/all/users/banger/X90M/GATE/HERMES_MPW/X901A_FR_TOPRIGHT_ALL_cropped_for_SEM.oas", 

        "layers": ["13.0"], 

        "ap1_template": "", 

        "ap1_mag": 45000, 

        "ap1_offset": [0.35, -4.4], 

        "ep_template": "", 

        "eps_template": "", 

        "magnification": 200000, 

        "mp_template": "X90M_GATE_PH", 

        "step": "PH", 

        "origin_x_y": "", 

        "step_x_y": "", 

        "n_cols_rows": "" 

    } 

} 
```
Also find it here: <mark>example_config.json</mark>

### User configuration file - Coordinate files

The following values are always mandatory: 
- **Layout database** (OASIS or GDSII) → `file path`
- **Layers** → a list of `stringified int or float`: in the format [“13.0”] or [“13.0”, “13.31”].  
(a list of at least one number - can be int or float - interest layers above visible layers) 
- **Magnification** → an `integer` 
- **Step** (process: litho (`PH`) or etch (`ET`) and `PH_HR`/`ET_HR` for high resolution)  
The mandatory values of a coordinate file parsing are visually represented by the following red boxes:  
![image showing importance of different parameters in json configuration](./pictures/Picture1.png "mandatory coordinate file json conf")

What is optionnal / non-mandatory: 
- **recipe_name** → a `string` 
(if none, recipe_name will be set to “recipe”) 
- **output_dir** → a `Path` (can be relative depending on the folder from where you run the CLI app)  
(if none, output_dir will be set under “/recipe_output” in the project’s architecture) 
- **coord_file** → a `Path`  
(depends on the type of recipe you make; coordinate file recipes opposed to opcfield recipes) 
- **Mp_template** à 3 possibilities:  
    1) an `empty string`/`""` (double quotation marks)  
    2) a single mp_template → `string`  
    3) a `pair of 1D/2D key-value` – refer to Fig.... below → `string: string` 
- **ap1_template** → a `string` 
- **ap1_mag** → an `int` 
- **ap1_offset** → a `list of float` (um) 
Relative value in um from the pattern coordinates to the addressing pattern. 
- **ep_template** → a `string` 
- **eps_template** → a `string` 
(if none, “EPS_Default“ would be default value)  
For a coordinate file parsing (non-opcfield) the mandatory values are showed in blue squares:  
![image showing importance of different parameters in json configuration](./pictures/Picture2.png "non mandatory coordinate file json conf")

### User configuration file - OPCField

For opcfield, `coord_file` field must be left empty but some opcfield parameters are still required in your json configuration file.

OPCField (depends on the type of recipe you make – opposed to file-based recipes) 

For OPCField recipes, all last 6 values are mandatory. No parser is required but the global mandatory values are still mandatory. All these values should be float or int if not empty like below. 

- **origin_x/y**: coordinates of the pattern on the bottom left corner (SEM referential ?) → `list of float`
- **step_x/y**: distance of a period, distance of a pattern to another (in um) → `list of int` 
- **n_cols/n_rows**: number of rows and columns of patterns in the opcfield → `list of int`

In the case of an opcfield, here are the mandatory values (red boxes):
![image showing importance of different parameters in json configuration](./pictures/Picture3.png "opcfield json conf")

## Commands 

> **_NOTE:_**
You can have help for your CLI usage with -h / --help attribute.  
Example (same thing for every command) ```spqr -h```

### Init
Creates either a generic configuration file for spqr, a coordinate file example or both.  
This command can be launched without argument, one of them two or both.

> **_NOTE:_**
Both commands will either generate a default file if a directory path is inputed as argument or create a file with given name if a file path is inputed as argument

We note 2 subcommands :

- `-c`, `--config_file`  
Taking a file or directory path.  
Creates a configuration file in JSON.  
Example : ```spqr upload -r /path/to/your/recipe.csv``` or ```spqr upload -r /directory/to/store/my/file/```
- `-x`, `--coordinate_file`  
Taking a file or directory path.  
Path (file or directory) to write a generic coordinate file (genepy format).  
Example : ```spqr upload -r /path/to/your/recipe.csv``` or ```spqr upload -r /directory/to/store/my/file/```

> **_NOTE:_**
By default, file are located in the directory you are running the command

### Build

Creates either a generic configuration file for spqr, a coordinate file example or both.  
This command should be launched, at least, with `-c` / `--user_config` argument.

We note 5 subcommands :

1) You are forced to use the `-c` / `--user_config` attribute since it should point to the file path where your recipe parameters are stored. The app manages if one or more recipes are stored in the file. It works without `-r` / `--user_recipe` only if one recipe is in the configuration file.  
Example : ```spqr build -c /path/to/your/conf_file.json```  

2) As soon as you have 2 recipes parameters stored in your `-c` file, you will need to define the `-r` / `--user_recipe` argument (to know which recipe config to launch). That is why this attribute is optional.  
The name provided here should match to the key of the dictionary referenced in your configuration file. Corresponding to your recipe with all its parameters in the curly brackets (pairs of key-value).  
Example : ```spqr build -c /path/to/your/conf_file.json -r P18_FGAT```

3) The `-l` / `--line_selection` attribute allows user to create a recipe based on one or more intervals.  
For example, if you want to select only the measurement points 50 to 60 (both included) you will need to write `-l 50-60`. If you want to add 70 to 80 you must write `-l 50-60 70-80`.  
Minimal example : ```spqr build -c /path/to/your/conf_file.json -l 50-60```  

4) The `-m` / `--measurement_file` attribute allows user to export the measurements as a csv file in the same directory as the exported recipe.  
Minimal example : ```spqr build -c /path/to/your/conf_file.json -m```

5) The `-u` / `--upload_rcpd` attribute allows user to upload the recipe created and the layout to RCPD.  
Minimal example : ```spqr build -c /path/to/your/conf_file.json -u```  

To sum up, you will at least use: 
```bash
spqr build -c path/to/your/config/file.json
```

All the other attributes (`-r`, `-l`, `-m` and `-u`) are optional and can be combined to the others in no particular order.  
As example: 
```bash
spqr build -c ./file.json -r my_recipe -l 50-60 70-80 -m -u
```

> **_NOTE:_**
The `-r` argument should match recipe name flagged in your json configuration file.  
Using example above, `my_recipe` should be a flag of recipe configuration in `./file.json` 

### Edit

The edit commands can help user modify a recipe on the fly. You can edit columns iterativelly in CLI by interaction. Editing columns in a specific row or the whole column.  
This command should be launched with all three arguments (`-r`, `-c` and `-n`).

We note 3 subcommands :  
- `-r`, `--recipe_file`  
Taking path of the HSS recipe to modify (.csv).  
Gets the recipe to edit.
- `-c`, `--config_file`  
Taking path of the user configuration file to modify (.json).  
Gets info of previously generated recipe / recipe you want to make.
- `-n`, `--recipe_name`  
Takes a string name of the recipe to edit (from config file).    
Selets the recipe within the configuration file.  

Example : ```spqr edit -r /path/to/your/recipe.csv -c ../path/to/your/config_file.json -n config_recipe_name```

> **_NOTE:_**
Each change on the recipe will have an impact on the naming of the edited recipe outputed (based on all the recipes in the folder). Adding one to the recipe version to differentiate them. If given recipe name is `recipe_name.csv` outputed name will be `recipe_name_1.csv`.

### Upload

The upload commands eases the sending process to RCPDirector machine (remote) for layouts or recipes.
This command should be launched by one of the two arguments (`-r` or `-l`).

> **_NOTE:_**
Beware what you upload as well as the size of files and their quantity.

We note 2 subcommands :  
- `-r`, `--recipe`  
Taking path to recipe.  
Uploads the given recipe to RCPDirector.  
Example : ```spqr upload -r /path/to/your/recipe.csv```
- `-l`, `--layout`  
Taking path to layout.
Uploads the given layout to RCPDirector.  
Example : ```spqr upload -l /path/to/your/layout.gds```

### Test
Originally intended for development purpose, the test command can help detect a bug in the recipe generation.

> **_NOTE:_**
The test command generates files from defined configuration files.

We note 2 subcommands :  
- `-r` / `--recipe`  
Taking arguments from `genepy`, `calibre_rulers`, `opcfield`, `csv` or `json`.  
Runs the selected recipe type in testing mode.  
Example : ```spqr test -r calibre_rulers```

- `-a`, `--all_recipes`  
Taking no arguments.  
Runs all (genepy,calibre_rulers,opcfield,csv,json) recipes types in testing mode.  
Example : ```spqr test -a```

## FAQ

**Can SPQR always make recipes like I would like to?**  
→ No, but it can help you gain time. Its goal is to cover the most generic usage of SEM recipe creation.