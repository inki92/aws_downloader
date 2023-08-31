"""EC2 Manager module"""

import boto3
import time
from retrying import retry
from config.conf import Config


class EC2Manager:
    """Class for manage aws ec2 instance."""
    def __init__(self, release, logger):
        self.release = release
        self.config = Config()
        self.client = self._create_ec2_client()
        self.logger = logger

    def _create_ec2_client(self):
        """
        Method for creating a Boto3 EC2 client.

        :return: class 'botocore.client.EC2'
        """
        return boto3.client('ec2',
                            aws_access_key_id=self.config.aws_access_key_id,
                            aws_secret_access_key=self.config.aws_secret_access_key,
                            aws_session_token=self.config.aws_token,
                            region_name=self.config.aws_region)

    def run_instance(self):
        """
        Method for running instance.

        :return: dict
        """
        ami_id_attr_name = f"ami_id_{self.release}"
        ami_id = getattr(self.config, ami_id_attr_name, None)
        return self.client.run_instances(
            ImageId=ami_id,
            InstanceType=self.config.instance_type,
            KeyName=self.config.key_pair_name,
            SecurityGroupIds=self.config.security_group_ids,
            MinCount=1,
            MaxCount=1
        )

    def get_instance_id(self, instance_dict):
        """
        Method for getting instance ID.

        :param instance_dict: dict
        :return: str
        """
        ec2_id = instance_dict['Instances'][0]['InstanceId']
        return ec2_id

    def get_instance_ip(self, ec2_id):
        ec2_ip = self.client.describe_instances(
            InstanceIds=[ec2_id])["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        return ec2_ip

    def terminate_instance(self, ec2_id):
        """
        Method for terminating instance.

        :param ec2_id: str
        """
        instance = self.client.terminate_instances(InstanceIds=[ec2_id])
        self.logger.info(f"Terminating instance {ec2_id} - "
                         f"Current state: {instance}")
        return ec2_id


class InstanceService:
    """Class for get info certain instance."""

    def __init__(self, release, logger):
        self.release = release
        self.logger = logger
        self.config = Config()
        self.ec2_manager = EC2Manager(self.release, self.logger)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def instance_start(self):
        """
        Method for run certain instance.

        :return: instance id (dict)
        """
        try:
            ec2_instance = self.ec2_manager.run_instance()
        except Exception:
            error_message = "Can't start instance."
            self.logger.error(error_message)
        instance_id = self.ec2_manager.get_instance_id(ec2_instance)
        self.logger.info(f"Instance ID is {instance_id}")
        return instance_id

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def instance_ip_address(self, instance_id):
        """
        Method for get ip address of certain instance.

        :return: instance ip (str)
        """
        try:
            instance_ip = self.ec2_manager.get_instance_ip(instance_id)
            self.logger.info(f"Instance IP is {instance_ip}")
            return instance_ip
        except Exception:
            error_message = f"Can't get instance ip address. {instance_ip}"
            self.logger.error(error_message)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def instance_terminate(self, instance_id):
        """Method for terminate certain instance."""
        try:
            output = (self.ec2_manager.terminate_instance(instance_id))
            self.logger.info(output)
        except Exception:
            error_message = f"Can't terminate instance {instance_id}"
            self.logger.error(error_message)


class Instance:
    """
    Class for manage certain instance without additional parameters.
    Callable from main script.
    """

    def __init__(self, release, logger):
        self.logger = logger
        self.instance = InstanceService(release, self.logger)
        self.instance_id = self.instance.instance_start()

    def instance_ip(self):
        """
        Method for get ip from certain running instance.

        :return: instance ip (str)
        """
        time.sleep(10)
        print(self.instance_id)
        instance_ip = self.instance.instance_ip_address(self.instance_id)
        return instance_ip

    def terminate(self):
        """Method for terminating from certain running instance."""
        self.instance.instance_terminate(self.instance_id)
