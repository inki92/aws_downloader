"""Check license module."""

from modules.ssh_client import SSHClient
import sys


class CheckLicense:
    """
    Class for comparison stable license file with possible new.
    """

    def __init__(self, logger, user, key_path, expected_license_hash, license_rpm, license_path):
        self.logger = logger
        self.ssh_client = SSHClient(self.logger)
        self.user = user
        self.expected_license_hash = expected_license_hash
        self.key_path = key_path
        self.license_rpm = license_rpm
        self.license_path = license_path

    def update_license(self, ip_address):
        """
        Method for update rpm package with license on the instance.

        :param ip_address: address of the instance
        """
        command = f'sudo dnf -y update {license_rpm}>>'
        self.logger.info(f"Updating {license_rpm} package.")
        self.ssh_client.execute_ssh_command(self.user,
                                            command, ip_address,
                                            self.key_path)

    def check_license(self, ip_address):
        """
        Method for comparison sha256 sums of license's.

        :param ip_address: address of the instance
        """
        self.update_license(ip_address)
        self.logger.info("Checking sha256sum of actual license")
        command = (f'sudo sha256sum P{self.license_path} |'
                   f' grep -q {self.expected_license_hash}')
        result = self.ssh_client.execute_ssh_command(self.user,
                                                     command, ip_address,
                                                     self.key_path)
        if result == 0:
            self.logger.info("License match to expected.")
        else:
            self.logger.error("WARNING!!! "
                              "License checksums do not match and was changed")
            sys.exit(1)

