"""Module for mount sshfs shared folder"""

import subprocess


class SSHFS():

    """Class for mount sshfs mount from instance to local machine."""
    def __init__(self, logger, user, pem_key_path, remote_path, local_path):
        self.logger = logger
        self.remote_path = remote_path
        self.local_path = local_path
        self.user = user
        self.pem_key_path = pem_key_path

    def check_sshfs_package(self):
        """
        Method for checking ssh rpm package was
        installed in the local system.

        package_name for rpm based = "fuse-sshfs"
        """
        package_name = "fuse-sshfs"
        try:
            subprocess.run(["rpm",  "-qa", package_name],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, check=True)
            self.logger.info(f"{package_name} is already installed.")
        except subprocess.CalledProcessError:
            self.logger.info(f"{package_name} is not installed. Installing...")
            self.install_sshfs_package(package_name)

    def install_sshfs_package(self, package_name):
        """
        Method for installation rpm package in the local system.

        :param package_name: name of rpm package.
        """
        install_command = ["sudo", "dnf", "install", "-y", package_name]
        try:
            subprocess.run(install_command, check=True)
            self.logger.info(f"{package_name} has been installed.")
        except Exception as e:
            error_message = f"Error: failed sshfs " \
                            f"rpm installation process."
            self.logger.error(error_message)

    def mount(self, ip_address):
        """
        Method for mount sshfs shared folder.

        :param ip_address: address of the destination.
        """
        self.check_sshfs_package()
        mount = f"sudo sshfs -o IdentityFile={self.pem_key_path} " \
                f"-o StrictHostKeyChecking=no " \
                f"{self.user}@{ip_address}:{self.remote_path} " \
                f"{self.local_path}"
        result = subprocess.run(mount, shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        if result.returncode == 0:
            self.logger.info(f"{self.local_path} "
                             f"is mounted to {self.remote_path}")
        else:
            self.logger.error(f"Error: {result.stderr.decode('utf-8')}")

    def unmount(self, mount_point):
        """Method for umount sshfs folder."""
        umount = f"sudo umount {self.mount_point}"
        try:
            subprocess.check_output(umount, shell=True)
            self.logger.info(f"Successfully unmounted {self.mount_point}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Unmount failed with error: {e}")
