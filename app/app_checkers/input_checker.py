from pathlib import Path
import json

# FIXME class ???
# TODO test anyway
#   To be a RET lib yes else fonctionnal no


class UserInputChecker:

    def __init__(self) -> None:
        self.file_extension_checker_instance = FileExtensionChecker()

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
                return numbers
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
        if not self.get_extension(filepath) == expected_extension:
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
                    raise ValueError(f"File {file_path} is not a genepy ssfile or is in bad format")
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
    #             raise ValueError(f"File {file_path} does not appear to be a CSV file or uses an unsupported delimiter.")
    #     except FileNotFoundError:
    #         raise ValueError(f"File {file_path} does not exist.")
    #     except Exception as e:
    #         raise ValueError(f"An error occurred while checking the file: {e}")

# TODO can we add .gds and .oasis files ?
