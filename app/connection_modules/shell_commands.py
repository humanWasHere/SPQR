import subprocess
from pathlib import Path

# TODO variabilize file to transfert
# see connection.py


def decorator_scp_rcpd(func):
    def wrapper(self, file_to_transfert, absolute_source_path=Path.cwd().parents[1] / "recipe_output", target_path="upguest@c2x20007.cr2.st.com:/home/DG/DGTransferData/DGUpload"):
        if not file_to_transfert.endswith(".csv"):
            raise ValueError("You did not import a correct CSV file. Check for extension.")
        return func(self, file_to_transfert, absolute_source_path, target_path)
    return wrapper


class ShellCommands:
    def __init__(self) -> None:
        pass

    @decorator_scp_rcpd
    def run_scp_command_to_rcpd(self, file_to_transfert, absolute_source_path, target_path):
        scp_command_arguments = ["scp", f"{absolute_source_path}/{file_to_transfert}", target_path]
        scp_command = ' '.join(scp_command_arguments)
        # TODO change print to subprocess -> uncomment
        print(scp_command)
        # Uncomment the following line to actually run the SCP command
        # command_result = subprocess.run(scp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # return command_result


# shell_commands_instance = ShellCommands()
# shell_commands_instance.run_scp_command_to_rcpd("recipe.csv")
