"""Module for enabling extra repositories on the instance."""

from modules.ssh_client import SSHClient
from retrying import retry


class EnableRepo:
    """Class for enabling repos on the EC2 instance."""

    def __init__(self, logger, user, key_path):
        self.logger = logger
        self.user = user
        self.key_path = key_path
        self.ssh_client = SSHClient(self.logger)

    def enable_repo(self, ip_address):
        """
        Method for enabling repos via sed.

        :param ip_address: ip of the instance.
        """
        command = "sudo sed -i 's/enabled=0/enabled=1/g' " \
                  "/etc/yum.repos.d/*repo"
        self.logger.info("Trying to enable all repositories:")
        self.ssh_client.execute_ssh_command(self.user,
                                            command, ip_address,
                                            self.key_path)

    def check_repo(self, ip_address):
        """
        Method for checking enabled repos on the instance.

        :param ip_address: ip of the instance.
        """
        command = "sudo dnf repolist enabled | grep -i source"
        result = self.ssh_client.execute_ssh_command(self.user,
                                                     command, ip_address,
                                                     self.key_path)
        if result != 0:
            self.logger.info("Repositories disabled, try to enable...")
        return result

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def enable_check(self, ip_address):
        """
        Combined method for one way enabling and checking repos.

        :param ip_address: ip of the instance.
        """
        self.enable_repo(ip_address)
        result = self.check_repo(ip_address)
        if result != 0:
            raise Exception("ERROR!!! Repositories can't be enabled.")
