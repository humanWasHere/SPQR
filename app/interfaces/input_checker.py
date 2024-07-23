import json
from pathlib import Path
from pydantic import BaseModel, ValidationError
from typing import List, Union, Dict, Optional

from ..parsers.json_parser import import_json


# /!\ should not exist ? type checking -> done w/ dedicated lib or dedicated class ?
class CheckConfig:
    def __init__(self, json_conf: dict) -> None:
        self.user_conf = json_conf
        self.recipe_name = json_conf['recipe_name']
        self.parser = Path(json_conf['parser'])
        self.layout = Path(json_conf['layout'])
        self.layers = json_conf['layers']
        self.mag = json_conf['magnification']
        self.mp_template = json_conf['mp_template']
        self.step = json_conf['step']

    # si on a l'info de quelle type de recette on traite avant le lancement de l'app
    def check_mandatory(self, check_parser):
        list_to_check = [self.layers, self.mag, self.mp_template, self.step]
        opcfield_list_to_check = ["opcfield_x", "opcfield_y", "step_x", "step_y", "num_step_x", "num_step_y"]
        assert Path(self.user_conf['output_dir']).exists()
        assert self.parser.exists()
        assert self.layout.exists()
        assert self.layout != ".", "One or more path mandatory elements seem empty in your user_config.json."
        assert all(element != "" for element in list_to_check), "One or more string mandatory elements seem empty in your user_config.json."
        assert not check_parser or self.parser != "", "The parser should not be an empty string."
        assert check_parser or all(isinstance(float(self.user_conf[element]), float) and self.user_conf[element] != "" for element in opcfield_list_to_check), "One or more opcfield mandatory elements are not floats or missing."

    def check_json(self):
        try:
            isinstance(self.user_conf, dict)
        except json.JSONDecodeError as e:
            raise ValueError("The provided configuration is not valid JSON.") from e
        return True

    def check_str(self):
        is_recipe_name_str = isinstance(self.recipe_name, str)
        is_mp_template_str = isinstance(self.mp_template, str)
        is_step_str = isinstance(self.step, str)
        return is_recipe_name_str and is_mp_template_str and is_step_str

    def check_int(self):
        is_mag_int = isinstance(self.mag, int)
        return is_mag_int

    def check_path(self):
        if not self.parser.exists():
            return False
        if not self.layout.exists():
            return False

    def check_layer_type(self):
        if not isinstance(self.layers, list):
            return False
        for layer in self.layers:
            if not isinstance(layer, str):
                return False
        # test for float
        return True

    def check_config(self, check_parser):
        self.check_mandatory(check_parser)
        self.check_json()
        self.check_str()
        self.check_int()
        self.check_path()
        self.check_layer_type()


class CheckConfigPydantic:
    # Modèle de base pour les paramètres communs
    class BaseRecipe(BaseModel):
        recipe_name: Optional[str] = None
        output_dir: Optional[str] = None
        layout: Path
        layers: List[Union[int, float]]
        magnification: int
        step: str | List[str]

        @classmethod
        def validate_step(cls, value):
            valid_steps = {"PH", "ET", "PH_HR", "ET_HR"}
            if value not in valid_steps:
                raise ValueError(f"Invalid step value: {value}. Must be one of {valid_steps}")
            return value

    # Modèle pour OPCfield
    class OPCfield(BaseRecipe):
        parser: Optional[str] = None
        ap1_template: Optional[str] = None
        ap1_mag: Optional[int] = None
        ep_template: Optional[str] = None
        eps_template: Optional[str] = None
        mp_template: Optional[Union[str, Dict[str, str]]] = None
        origin_x_y: List[float]
        step_x_y: List[int]
        n_rows_cols: List[int]
        ap1_offset: List[float]

    # Modèle pour un autre type de recette (exemple)
    class GenepyCalibreRulers(BaseRecipe):
        parser: str

    # Fonction pour charger et valider le fichier JSON
    @staticmethod
    def validate_json_file(json_config_content: dict, recipe_type_start: str | Path | None, user_recipe_build: str | None):
        if recipe_type_start is None:
            try:
                data = json_config_content[user_recipe_build]
                recipe = CheckConfigPydantic.BaseRecipe(**data)
                return recipe
            except ValidationError as e:
                print("Erreur de validation:", e)
            except Exception as e:
                print("Une erreur s'est produite:", e)
        else:
            try:
                data = json_config_content[recipe_type_start]
                # ['genepy', 'calibre_rulers', 'csv', 'json']
                if recipe_type_start == "genepy" or recipe_type_start == "calibre_rulers":
                    recipe = CheckConfigPydantic.GenepyCalibreRulers(**data)
                elif recipe_type_start == "opcfield":
                    recipe = CheckConfigPydantic.OPCfield(**data)
                # TODO make validator for csv and json recipes
                else:
                    raise ValueError(f"Unknown recipe type: {recipe_type_start}")
                return recipe
            except ValidationError as e:
                print("Erreur de validation:", e)
            except Exception as e:
                print("Une erreur s'est produite:", e)


class UserInputChecker:

    def __init__(self) -> None:
        self.file_extension_checker_instance = FileExtensionChecker()  # TODO actually use it
        self.input_source = InputSourceValidator()

    def get_secured_user_filepath(self, message) -> str:
        while True:
            file_path_str = input(message)
            file_path = Path(file_path_str)
            if not file_path.exists():
                print('The file does not exist. Please try again.')
            elif not file_path.is_file():
                print('The path is not a valid file. Please try again.')
            return str(file_path)

    def get_secured_user_list_int_float(self, message) -> list:
        while True:
            list_input = input(message)
            try:
                numbers = []
                for layer in list_input.split(', '):
                    stripped_layer = layer.strip()
                    try:
                        number = int(stripped_layer)
                    except ValueError:
                        number = float(stripped_layer)
                    numbers.append(str(number))
                return list(numbers)
            except ValueError:
                print("Invalid input for layers. Please enter a list of numbers separated by commas.")


class FileExtensionChecker:

    def __init__(self) -> None:
        pass

    def get_extension(self, file_path) -> str:
        string_parts = str(file_path).rsplit('.', 1)
        if len(string_parts) > 1:
            return string_parts[-1]
        else:
            raise ValueError("No file extension was detected")

    def simple_filepath_extension_checker(self, filepath, expected_extension) -> None:
        if self.get_extension(filepath) != expected_extension:
            # TODO change it
            print(f"File extension is not {expected_extension} !")
            # raise ValueError(f"File extension is not {expected_extension} !")
        return None


class InputSourceValidator:

    def __init__(self) -> None:
        pass

    def genepy_ssfile_checker(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                if not "X_coord_Pat" and "Name" in file:
                    raise ValueError(f"File {file_path} is not a genepy file or is in bad format")
        except FileNotFoundError:
            raise ValueError(f"File {file_path} does not exist.")
        except Exception as e:
            raise ValueError(f"An error occurred while checking the file: {e}")

    def json_checker(self, file_path):
        try:
            # json.load(file)  # try -> if not -> not a json
            for line in file_path:
                line = line.strip()
                if line:  # If the line is not empty after stripping whitespace
                    if line[0] == "{":
                        return  # The file starts with a curly brace, so it might be a JSON object
                    else:
                        break
        except FileNotFoundError:
            raise ValueError(f"File {file_path} does not exist.")
        except json.JSONDecodeError:
            raise ValueError(f"File {file_path} is not a json or is in bad format")
        except Exception as e:
            raise ValueError(f"An error occurred while checking the file: {e}")

    def csv_checker(self, file_path):
        try:
            first_line = file_path.readline()
            if ',' not in first_line:
                raise ValueError(f"File {file_path} is not a .csv or is in bad format")
        except FileNotFoundError:
            raise ValueError(f"File {file_path} does not exist.")
        except Exception as e:
            raise ValueError(f"An error occurred while checking the file: {e}")

    # import csv
    # def csv_file_content_checker(self, file_path, delimiters=',;\t'):
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             # Try reading the file with different delimiters
    #             for delimiter in delimiters:
    #                 file.seek(0)  # Reset file pointer to the beginning
    #                 reader = csv.reader(file, delimiter=delimiter)
    #                 try:
    #                     rows = list(reader)
    #                     # If we can read more than one row, it's likely a CSV file
    #                     if len(rows) > 1:
    #                         return
    #                 except csv.Error:
    #                     # This delimiter did not work, try the next one
    #                     continue
    #             raise ValueError(f"File {file_path} does not appear to be a CSV file"
    #                              "or uses an unsupported delimiter.")
    #     except FileNotFoundError:
    #         raise ValueError(f"File {file_path} does not exist.")
    #     except Exception as e:
    #         raise ValueError(f"An error occurred while checking the file: {e}")

# TODO can we add .gds and .oasis files ?
