from pathlib import Path
import ast

# FIXME class ???


class UserInputChecker:

    # def __init__(self, user_input) -> None:
    #     self.input_to_check = user_input

    def __init__(self) -> None:
        pass

    def get_secured_user_file_path(self, message) -> str:
        while True:
            file_path_str = input(message)
            file_path = Path(file_path_str)
            if not file_path.exists():
                print('The file does not exist. Please try again.')
            elif not file_path.is_file():
                print('The path is not a valid file. Please try again.')
            else:
                return str(file_path)

    # def get_secured_user_int_float_list(self, message) -> list:
    #     while True:
    #         list_input = input(message)
    #         try:
    #             result = ast.literal_eval(list_input)
    #             if isinstance(result, list) and all(isinstance(item, (int, float)) for item in result):
    #                 return [float(item) for item in result]
    #             else:
    #                 print("Please enter a list of numbers (integers or floats) separated by commas (e.g., '1, 2.5, 3').")
    #         except (ValueError, SyntaxError):
    #             print("Invalid input. Please enter a valid list of numbers (integers or floats) separated by commas (e.g., '1, 2.5, 3').")

    def get_secured_user_int_float_list(self, message) -> list:
        while True:
            list_input = input(message)
            try:
                # Crée une liste de nombres en convertissant chaque élément en entier ou en flottant
                numbers = []
                for layer in list_input.split(', '):
                    stripped_layer = layer.strip()
                    try:
                        # Essaye d'abord de convertir en entier
                        number = int(stripped_layer)
                    except ValueError:
                        # Si la conversion en entier échoue, essaye de convertir en flottant
                        number = float(stripped_layer)
                    numbers.append(str(number))
                return numbers
            except ValueError:
                print("Invalid input for layers. Please enter a list of numbers separated by commas.")
