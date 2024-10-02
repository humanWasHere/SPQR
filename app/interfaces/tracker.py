import argparse
from datetime import datetime
from dotenv import load_dotenv
import logging
import os
import pandas as pd
from pathlib import Path

from .logger import logger_init  # import first

from ..parsers.parse import FileParser


# def check_env_is_prod(tracker_name) -> bool:
#     """check_env_is_prod is a function that checks if the global environment is development or production."""
#     if ENVIRONMENT != "production":
    # if ENVIRONMENT != "development":
#         logging.warning(f"{tracker_name} tracker only works in production !")
#         return False
#     else:
#         return True


# def setup_tracker(csv_filename: str, default_columns: list) -> pd.DataFrame:
#     """setup_tracker is a fonction that is reused in most tracker.
#     It gets current date and defines as DataFrame with months as rows."""
#     # Get current date
#     now = datetime.now()
#     current_year = now.year
#     current_month = now.strftime("%B").lower()

#     # Create DataFrame
#     csv_tracker_path = os.getenv("CSV_TRACKER_PATH")
#     if not csv_tracker_path:
#         logging.error("CSV_TRACKER_PATH n'est pas défini dans les variables d'environnement.")
#     csv_tracker_path = Path(csv_tracker_path) / f"{csv_filename}_{current_year}.csv"
#     if csv_tracker_path.exists():
#         tracker_dataframe = pd.read_csv(csv_tracker_path, index_col=0)
#     else:
#         tracker_dataframe = pd.DataFrame(columns=default_columns,
#                                          index=["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"])
#         tracker_dataframe.loc[:, :] = 0

#     return tracker_dataframe, csv_tracker_path, current_month, current_year

# previous main function
# # valid_command_list = ["-v", "build", "test", "init", "-c", "-r", "-u", "-l", "-m", "-a", "-j", "-t"]
# valid_command_list = get_commands_cli(cli())
# # separator
# tracker_key_value_to_input = {
#     "spqr_recipe_launched_tracker": ["launched_recipes"],
#     "spqr_user_tracker": [],
#     "spqr_parser_tracker": ['HSSParser', 'TACRulerParser', 'JSONParser', 'OPCFieldReverse', 'SSFileParser', 'CalibreXMLParser'],
#     "spqr_cli_command_tracker": valid_command_list
# }
# # dict of tracker init
# dict_of_trackers = {}
# for tracker, tracker_columns_list in tracker_key_value_to_input.items():
#     unpacked_values = setup_tracker(tracker, tracker_columns_list)
#     tracker_dataframe, csv_tracker_path, current_month = unpacked_values[:3]
#     if tracker_dataframe is None:
#         return
#     dict_of_trackers[tracker] = tracker_columns_list
# return dict_of_trackers


# def launched_recipe_tracker():
#     """launched_recipe_tracker is a function that counts the number of recipe launched and stores it in a file."""
#     if check_env_is_prod("launched recipe"):
#         unpacked_values = setup_tracker("spqr_recipe_launched_tracker", ["launched_recipes"])
#         tracker_dataframe, csv_tracker_path, current_month = unpacked_values[:3]
#         if tracker_dataframe is None:
#             return
#         tracker_dataframe.at[current_month, "launched_recipes"] += 1
#         tracker_dataframe.to_csv(csv_tracker_path)
#         return tracker_dataframe


# def user_tracker() -> None:
#     """user_tracker is a function that counts the number of use of each member of the team throughout time."""
#     if check_env_is_prod("user"):
#         unpacked_values = setup_tracker("spqr_user_tracker", [])
#         tracker_dataframe, csv_tracker_path, current_month = unpacked_values[:3]
#         if tracker_dataframe is None:
#             return
#         current_user = os.getlogin()
#         if current_user not in tracker_dataframe.columns:
#             tracker_dataframe[current_user] = 0
#         tracker_dataframe.at[current_month, current_user] += 1
#         tracker_dataframe.to_csv(csv_tracker_path)
#         return tracker_dataframe


# def parser_tracker(current_parser) -> None:
#     """parser_tracker is a function that counts the kind of parser used throughout time."""
#     if check_env_is_prod("parser"):
#         unpacked_values = setup_tracker("spqr_parser_tracker", ['HSSParser', 'TACRulerParser', 'JSONParser', 'OPCFieldReverse', 'SSFileParser', 'CalibreXMLParser'])
#         tracker_dataframe, csv_tracker_path, current_month = unpacked_values[:3]
#         if tracker_dataframe is None:
#             return
#         if current_parser not in tracker_dataframe.columns:
#             logging.error(f"Parser {current_parser} n'est pas défini dans les colonnes du DataFrame.")
#         tracker_dataframe.at[current_month, current_parser] += 1
#         tracker_dataframe.to_csv(csv_tracker_path)
#         return tracker_dataframe


# def cli_command_tracker(command_executed) -> None:
#     # TODO change logic so that it covers all subcommands according commands
#     """cli_command_tracker is a function that counts the CLI commands used throughout time."""
#     if check_env_is_prod("CLI command"):
#         valid_command_list = ["-v", "build", "test", "init", "-c", "-r", "-u", "-l", "-m", "-a", "-j", "-t"]
#         unpacked_values = setup_tracker("spqr_cli_command_tracker", valid_command_list)
#         tracker_dataframe, csv_tracker_path, current_month = unpacked_values[:3]
#         if tracker_dataframe is None:
#             return
#         # valid_command_list = command_list + ["--version", "--user_config", "--user_recipe", "--upload_rcpd", "--line_selection", "--mesurement_file", "--recipe", "--all_recipes", "--config_file", "--coordinate_file"]
#         for command in command_executed:
#             if command in valid_command_list:
#                 tracker_dataframe.at[current_month, command] += 1
#         # command_mapper = {
#         #     "--version": "-v",
#         #     "--user_config": "-c",
#         #     "--user_recipe": "-r",
#         #     "--upload_rcpd": "-u",
#         #     "--line_selection": "-l",
#         #     "--mesurement_file": "-m",
#         #     "--recipe": "-r",
#         #     "--all_recipes": "-a",
#         #     "--config_file": "-j",
#         #     "--coordinate_file": "-t"
#         # }
#         # for command, simplified_command in command_mapper.items():
#         #     if command in command_executed:
#         #         tracker_dataframe.at[current_month, command_mapper[command]] += 1
#         tracker_dataframe.to_csv(csv_tracker_path)
#         return tracker_dataframe


# WARNING : not to call in a recipe since it reads Log files
def log_metrics() -> None:
    """must be used manually for dev purpose."""
    # should be used in dev env in this state
    tracker_dataframe, csv_tracker_path, current_month, current_year = setup_tracker("spqr_log_metrics", ["error", "debug", "info"])
    if tracker_dataframe is None:
        return
    tracker_dataframe.loc[:, :] = 0

    log_file = Path(__file__).resolve().parents[2] / "spqr.log"
    if not log_file.exists():
        logging.error(f"Log file {log_file} does not exist.")
        return

    log_file_content = log_file.read_text().splitlines()

    # Fonction pour traiter les lignes de log
    def process_log_line(line, log_type) -> None:
        log_date = line.split()[0]
        log_year, log_month = log_date.split('/')[2], log_date.split('/')[1]
        if int(log_year) == int(current_year):
            month_name = pd.Timestamp(year=int(log_year), month=int(log_month), day=1).strftime("%B").lower()
            if month_name in tracker_dataframe.index:
                tracker_dataframe.at[month_name, log_type] += 1

    # Parcourir le contenu du fichier de log
    for line in log_file_content:
        if "[ERROR]" in line:
            process_log_line(line, "error")
        elif "[DEBUG]" in line:
            process_log_line(line, "debug")
        elif "[INFO]" in line:
            process_log_line(line, "info")
    #     if command in command_executed:
    #         tracker_dataframe.at[current_month, command_mapper[command]] += 1
    tracker_dataframe.to_csv(csv_tracker_path)


# class TrackerMetrics():
#     def __init__(self):
#         if check_env_is_prod():
    #         self.start_recipe_gen = False
    #         result = setup_tracker("spqr_passing_recipe_tracker", ["launched_recipes", "passed_recipes", "failed_recipes_deduction"])
    #         self.tracker_dataframe, self.csv_tracker_path, self.current_month = result[:3]
    #         if self.tracker_dataframe is None:
    #             logging.error("Tracker dataframe is empty")

#     def check_for_failed_recipes(self) -> None:
#         logic = self.tracker_dataframe.at[self.current_month, "launched_recipes"] - self.tracker_dataframe.at[self.current_month, "passed_recipes"]
#         if self.tracker_dataframe.at[self.current_month, "failed_recipes_deduction"] + 1 == logic:
#             self.tracker_dataframe.at[self.current_month, "failed_recipes_deduction"] += 1
#             self.tracker_dataframe.at[self.current_month, "passed_recipes"] -= 1
#         else:
#             logging.error("Failed recipes number is not coherent")
#         # if this method is launched, it means the recipe creation has started
#         # set after failed recipes checking to not influence it
#         self.tracker_dataframe.at[self.current_month, "launched_recipes"] += 1
#         self.tracker_dataframe.to_csv(self.csv_tracker_path)

#     def passed_recipes_tracker(self) -> None:
#         self.tracker_dataframe.at[self.current_month, "passed_recipes"] += 1
#         self.tracker_dataframe.to_csv(self.csv_tracker_path)


# TODO do log monitoring --> original goal is to monitor recipe fail or pass


def define_file_path_from_env() -> Path | None:
    load_dotenv()
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    if ENVIRONMENT:
        csv_tracker_path = os.getenv(f"CSV_TRACKER_PATH_{ENVIRONMENT.upper()}")
        if csv_tracker_path:
            return Path(csv_tracker_path) / f"spqr_global_data_tracker_{datetime.now().year}_{os.getenv('ENVIRONMENT')}.csv"
        else:
            logging.error(f"CSV_TRACKER_PATH_{ENVIRONMENT} n'est pas défini dans les variables d'environnement.")
    else:
        logging.error("Global tracker has not recognized environment !")


def global_data_tracker(parser: FileParser | None, cli_arguments: dict) -> pd.DataFrame:
    """Here we set a dict of df to gather all tracker information."""
    # /!\ This method doesn't capture -v and -h commands
    def parse_argparse_arguments() -> list:
        cli_arguments_list_formatted = []
        cli_arguments_list_formatted.append(cli_arguments['running_mode'])
        if len(cli_arguments) > 1:
            cli_arguments_key_list = list(cli_arguments.keys())
            cli_arguments_value_list = list(cli_arguments.values())
            for argument_place_number_in_list in range(1, len(cli_arguments)):
                if cli_arguments_value_list[argument_place_number_in_list] is not False:
                    if cli_arguments_key_list[argument_place_number_in_list] == "recipe":
                        cli_arguments_list_formatted.append(f"{cli_arguments_key_list[argument_place_number_in_list]}-{cli_arguments_value_list[argument_place_number_in_list]}")
                    else:
                        cli_arguments_list_formatted.append(f"{cli_arguments_key_list[argument_place_number_in_list]}")
        return cli_arguments_list_formatted

    # if check_env_is_prod("global_tracker"):
    # get line info
    current_date = datetime.now().strftime('%d-%m-%Y')
    current_username = os.getlogin()
    if cli_arguments['running_mode'] in ["init", "edit", "upload"]:
        parser = "Unused in this case"
    used_commands = parse_argparse_arguments()
    data = {
        'Date': [current_date],
        'Username': [current_username],
        'Parser': [parser],
        'Commands': [used_commands]
    }
    # Create DataFrame
    csv_tracker_path = define_file_path_from_env()
    new_row = pd.DataFrame(data)
    new_row['Date'] = pd.to_datetime(new_row['Date'], dayfirst=True, format='%d-%m-%Y').dt.date
    new_row.set_index('Date', inplace=True)
    if csv_tracker_path.exists():
        # two following lines are for debug purpose
        # tracker_dataframe = pd.read_csv(csv_tracker_path, index_col='Date', parse_dates=True)
        # tracker_dataframe.index = tracker_dataframe.index.date
        tracker_dataframe = pd.read_csv(csv_tracker_path, index_col="Date")
        tracker_dataframe = pd.concat([tracker_dataframe, new_row])
    else:
        tracker_dataframe = new_row
    tracker_dataframe.to_csv(csv_tracker_path)
    return tracker_dataframe

# def extract_launched_recipe_number() -> pd.DataFrame:
#     tracker_dataframe = pd.read_csv(csv_tracker_path, index_col="Date")


def run_tracker_data_extraction():
    # parse whole dataframe csv
    # extract_launched_recipe_number()
    # extract_recipe_launched_by_user()
    # extract_parser_usage()
    # extract_command_usage()
    pass
