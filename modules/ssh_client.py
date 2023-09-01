"""SSH client module"""

import paramiko
from retrying import retry


class SSHClient:

    """Class for connect to instance via ssh."""
    def __init__(self, logger):
        self.logger = logger

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def execute_ssh_command(self, user, command, ip_address, key_path):
        """
        Method for SSH connect to EC2 instance.

        :param command:: str
        :param ip_address:: str
        :param key_path:: str
        :return: None
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ip_address,
                               username=user,
                               key_filename=key_path)
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            self.logger.info(output)
            status_code = stdout.channel.recv_exit_status()
            if status_code != 0:
                self.logger.error(f"Error: Can't execute \"{command}\" by SSHClient. Trying...")
                raise Exception
            return status_code
        except Exception as error:
            raise error
        finally:
            ssh_client.close()

    def copy_file_from_ec2_to_local(self, user, ip_address,
                                    key_path, source_path,
                                    destination_path):
        """
        This method using sftp module of paramiko to copy
        the file from the EC2 instance to your local machine.

        :param: ip_address: str
        :param: key_path: str
        :param: source_path: str
        :param: destination_path: str
        :return: None
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(hostname=ip_address,
                               username=user,
                               key_filename=key_path)
            sftp_client = ssh_client.open_sftp()
            sftp_client.get(source_path, destination_path)
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            sftp_client.close()
            ssh_client.close()