from datetime import datetime
from dotenv import load_dotenv
import logging
import os
import pandas as pd
from pathlib import Path
import socket

from ..parsers.parse import FileParser


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


def parse_global_data_tracker():
    csv_tracker_path = define_file_path_from_env("GLOBAL_DATA_TRACKER")
    if not csv_tracker_path.exists():
        return
    else:
        return pd.read_csv(csv_tracker_path, index_col="Date")


def define_file_path_from_env(file_name_env) -> Path | None:
    load_dotenv()
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    if ENVIRONMENT:
        csv_file_path = os.getenv(f"{file_name_env}_{ENVIRONMENT.upper()}")
        if csv_file_path:
            return Path(csv_file_path) / f"spqr_{file_name_env.lower()}_{datetime.now().year}_{str(ENVIRONMENT.lower())}.csv"
        else:
            logging.error(f"{file_name_env} n'est pas défini dans les variables d'environnement.")
    else:
        logging.error(f"{__file__} does not recognizes environment !")


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

    # get line info
    current_date = datetime.now().strftime('%d-%m-%Y')
    current_username = os.getlogin()
    hostname = socket.gethostname()  # fqdn = socket.getfqdn()
    operating_system = "Unix" if os.name == 'posix' else "Windows" if os.name == 'nt' else "Unknown"
    if cli_arguments['running_mode'] in ["init", "edit", "upload"]:
        parser = "Unused in this case"
    used_commands = parse_argparse_arguments()
    data = {
        'Date': [current_date],
        'OS': [operating_system],
        'Hostname': [hostname],
        'Username': [current_username],
        'Parser': [parser],
        'Commands': [used_commands]
    }
    # Create DataFrame
    csv_tracker_path = define_file_path_from_env("GLOBAL_DATA_TRACKER")
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


# TODO add month as argument of functions
def extract_app_usage(username: str | None = None, include_all_commands: bool = False) -> pd.DataFrame:
    """extracts data from the global_data_tracker df related to user(s), recipe launched or app usage"""
    global_data_tracker_df = parse_global_data_tracker()
    index_as_a_column = global_data_tracker_df.reset_index()
    working_df = index_as_a_column[["Date", "Username", "Commands"]]
    if username is not None:
        working_df = working_df[working_df['Username'] == username]
    if include_all_commands:
        number_of_recipe_launched = working_df['Commands'].apply(lambda commands_list: 'test' in commands_list or 'build' in commands_list).sum()
        return f"{number_of_recipe_launched} recipe(s) have been launched by {'all users' if username is None else username} this year"
    else:
        return f"app has been used {working_df.shape[0]} times by {'all users' if username is None else username} this year"


def extract_environment(environment: str | None = None):
    """extracts os and machine data from global_data_tracker df"""
    global_data_tracker_df = parse_global_data_tracker()
    index_as_a_column = global_data_tracker_df.reset_index()
    working_df = index_as_a_column[["Date", "OS", "Hostname"]]
    return f"app has been used {working_df.shape[0]} times by {'all users' if username is None else username} this year"


def extract_parser_usage():
    """extracts parser info from global_data_tracker"""
    global_data_tracker_df = parse_global_data_tracker()
    index_as_a_column = global_data_tracker_df.reset_index()
    working_df = index_as_a_column[["Date", "Parser"]]


# def extract_launched_recipe_number() -> pd.DataFrame:
#     tracker_dataframe = pd.read_csv(csv_tracker_path, index_col="Date")


def run_tracker_data_extraction():
    extract_app_usage()
    # extract_launched_recipe_number()
    # extract_parser_usage()
    # extract_command_usage()
    pass
