class UserInputChecker:

    def __init__(self, user_input) -> None:
        self.input_to_check = user_input

    def check_input_is_list(self):
        if self.input_to_check is not ...:
            raise ValueError("user input is not a list !")
        else:
            pass


# import ast

# def is_input_a_list(user_input):
#     try:
#         # Safely evaluate the input string
#         result = ast.literal_eval(user_input)
#         # Check if the result is a list
#         return isinstance(result, list)
#     except (ValueError, SyntaxError):
#         # A ValueError or SyntaxError indicates that the input wasn't a valid Python literal
#         return False

# # Get user input
# user_input = input("Enter a list: ")

# # Check if the input is a list
# if is_input_a_list(user_input):
#     print("The input is a list.")
# else:
#     print("The input is not a list.")
# _______________________________________________
# from pathlib import Path

# # Replace this with the path you want to check
# file_path = Path("/path/to/your/file.txt")

# # Check if the path is valid and the file exists
# if file_path.exists() and file_path.is_file():
#     print(f"The file '{file_path}' exists and is a valid file path.")
# else:
#     print(f"The file '{file_path}' does not exist or is not a valid file path.")
