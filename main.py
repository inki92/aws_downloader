"""Main script"""
import config.conf as config
from logger.logger import Logger
from modules.ec2_manager import EC2Manager
from modules.ssh_client import SSHClient
from remote_functions.check_license import CheckLicense
from remote_functions.sshfs import SSHFS
from remote_functions.enable_repo import EnableRepo

# from modules.ec2_manager import Instance
from modules.gcp_manager import GCPManager


if __name__ == "__main__":
  logger_instance = Logger()
  logger = logger_instance.logger
  check_license = CheckLicense(logger,
                            config.instance_user,
                            config.private_key_path,
                            config.expected_license_hash,
                            config.license_rpm,
                            config.license_path)
  sshfs = SSHFS(logger, config.instance_user, config.private_key_path,
                config.instance_mount_dir, config.local_mount_dir)
  enable_repo = EnableRepo(logger, config.instance_user, config.private_key_path)

# INSTANCE MANAGER START
  instance_9 = GCPManager(9, logger)
  instance_9.run_instance()
  instance_ip = instance_9.instance_ip()

# NEW REMOTE FUNCTIONS START
  try:
    check_license.check_license(instance_ip)
    enable_repo.enable_check(instance_ip)
    sshfs.mount(instance_ip)
  except:
    instance_9.terminate()
    print("INSTANCE DOWN")



