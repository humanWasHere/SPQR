import argparse
import logging
import os
import socket
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from ..parsers.parse import FileParser


def parse_global_data_tracker():
    csv_tracker_path = define_file_path_from_env("GLOBAL_DATA_TRACKER")
    if not csv_tracker_path.exists():
        return
    else:
        return pd.read_csv(csv_tracker_path, index_col="Date")


def define_file_path_from_env(file_name_env) -> Path | None:
    load_dotenv()
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    csv_file_path = os.getenv(file_name_env)
    if not ENVIRONMENT:
        logging.debug(f"{__file__} does not recognize environment !")
    if csv_file_path:
        file_name = f"spqr_{file_name_env.lower()}_{datetime.now().year}_{ENVIRONMENT.lower()}.csv"
        return Path(csv_file_path) / file_name
    logging.error(f"{file_name_env} n'est pas défini dans les variables d'environnement.")
    return Path(os.devnull)


def global_data_tracker(parser: FileParser | None, cli_args: argparse.Namespace) -> pd.DataFrame:
    """
    Append all tracking information to a central log file using pandas.
    Does not capture -v and -h commands"""
    def parse_argparse_arguments(arguments: argparse.Namespace) -> list:
        cli_arguments = vars(arguments).copy()
        mode = cli_arguments.pop('running_mode')
        arg_list = [mode]
        if mode == 'test' and cli_arguments['recipe']:
            arg_list.append('recipe-' + cli_arguments.pop('recipe'))
        remaining_args = [key for key, value in cli_arguments.items() if value]
        arg_list.extend(remaining_args)
        return arg_list

    # get line info
    current_date = datetime.now().strftime('%d-%m-%Y')
    current_username = os.getlogin()
    hostname = socket.gethostname()  # fqdn = socket.getfqdn()
    if os.name == 'posix':
        import distro
        operating_system = f"{distro.id()}_{distro.version()}"
    elif os.name == 'nt':
        operating_system = "Windows"
    else:
        operating_system = "Unknown"

    if cli_args.running_mode in ["init", "edit", "upload"]:
        parser = "NA"
    used_commands = parse_argparse_arguments(cli_args)
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


def extract_environment(username: str | None = None):
    """extracts os and machine data from global_data_tracker df"""
    global_data_tracker_df = parse_global_data_tracker()
    index_as_a_column = global_data_tracker_df.reset_index()
    working_df = index_as_a_column[["Date", "OS", "Hostname"]]
    return f"app has been used {working_df.shape[0]} times by {username or 'all users'} this year"


def extract_parser_usage():
    """extracts parser info from global_data_tracker"""
    global_data_tracker_df = parse_global_data_tracker()
    index_as_a_column = global_data_tracker_df.reset_index()
    working_df = index_as_a_column[["Date", "Parser"]]
    return working_df


# def extract_launched_recipe_number() -> pd.DataFrame:
#     tracker_dataframe = pd.read_csv(csv_tracker_path, index_col="Date")


def run_tracker_data_extraction():
    extract_app_usage()
    # extract_launched_recipe_number()
    # extract_parser_usage()
    # extract_command_usage()
    pass
