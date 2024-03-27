import subprocess
from pathlib import Path

# see connection.py
# FIXME scp slower than rsync but more secured (uses SSH by default)
#  see : https://stackoverflow.com/questions/20244585/how-does-scp-differ-from-rsync


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
        # scp_command = ' '.join(scp_command_arguments)
        # print(scp_command)
        # TODO Uncomment the following line to actually run the SCP command
        try:
            command_result = subprocess.run(scp_command_arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"File {file_to_transfert} transferred successfully to {target_path}.")  # check it on RCPDirector instead ?
            return command_result
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while transferring {file_to_transfert}: {e}")
            return None
