"""Download package module"""

import re
from modules.ssh_client import SSHClient


class DownloadPackage():
    """Class for downloading rpm on the instance."""

    def __init__(self, logger, path_to_download, user, key_path, package_name):
        self.logger = logger
        self.package_name = package_name
        self.path_to_download = path_to_download
        self.user = user
        self.key_path = key_path
        self.ssh_client = SSHClient(self.logger)

    def create_path(self, ip_address):
        """
        Method for create directory for download rpm's.

        self.path_to_download = instance_mount_dir in config.
        :param ip_address: address of the instance
        :return: status
        """
        command = (f'sudo mkdir {self.path_to_download}')
        self.logger.info("Trying to create directory for download packages:")
        result = self.ssh_client.execute_ssh_command(self.user, command, ip_address, self.key_path)
        if result == 0:
            self.logger.info(f"Directory {self.path_to_download} created.")
        else:
            self.logger.error(f"Can't create directory {self.path_to_download}. Trying...")
        return result

    def check_directory(self, ip_address):
        """
        Method for check directory on the instance.

        self.path_to_download = instance_mount_dir in config.
        :param ip_address: address of the instance
        :return: status
        """
        try:
            command = (f'sudo ls {self.path_to_download}')
            result = self.ssh_client.execute_ssh_command(self.user,
                                                         command, ip_address,
                                                         self.key_path)
            if result == 0:
                self.logger.info(f"Directory exists: {self.path_to_download}")
            return result
        except Exception as e:
            self.logger.error(f"Can't create directory {self.path_to_download}.")
            raise e

    def download_command(self, ip_address, package_name):
        """
        Method for download rpm package to the instance.

        :param ip_address: address of the instance
        :param package_name: name of the rpm package
        :return: status
        """
        try:
            # create downloadable name of the package
            if package_name.endswith(".src.rpm"):
                package_name_cut = package_name.replace('.src.rpm', '')
                command = (
                    f"sudo dnf download {package_name_cut} --source --downloaddir={self.path_to_download} --setopt=*.module_hotfixes=1")
                result = self.ssh_client.execute_ssh_command(self.user, command, ip_address, self.key_path)
            else:
                package_name_cut = package_name.replace('.rpm', '')
                command = (
                    f"sudo dnf download {package_name_cut} --downloaddir={self.path_to_download} --setopt=*.module_hotfixes=1")
                result = self.ssh_client.execute_ssh_command(self.user, command, ip_address, self.key_path)

            if result == 0:
                self.logger.info(f"Successfully downloaded {package_name} ...")
            return result
        except:
            self.logger.error(f"Can't download {package_name}")

    def download_package(self, ip_address, package_name):
        """
        Method for create path and download rpm package to the instance.

        :param ip_address: address of the instance
        :param package_name: name of the rpm package
        :return: status
        """

        check_dir_result = self.check_directory(ip_address)
        if check_dir_result != 0:
            self.create_path(ip_address)
        self.download_command(ip_address, package_name)
