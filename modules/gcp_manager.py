from googleapiclient import discovery
from google.oauth2 import service_account
from google.cloud import compute_v1
from google.api_core.extended_operation import ExtendedOperation
import os
import time
from retrying import retry

import config.conf as config

# Setup default creds environment variables
credentials_path = "config/credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


class GCPManager:

    """Class for managing Google Cloud Project instances."""

    def __init__(self, release, logger):
        self.release = release
        self.logger = logger
        self.project_id = config.project_id
        self.zone = config.zone
        self.region = config.region
        self.instance_name = config.instance_name
        self.machine_type = config.machine_type
        self.family = config.family
        self.image_project = config.project
        self.subnetwork = config.subnetwork

    def get_image_from_family(self):
        """
        Retrieve the newest image that is part of a given family in a project.

        Args:
            project: project ID or project number of the
            Cloud project you want to get image from.
            family: name of the image family you want to get image from.

        Returns:
            An Image object.
        """

        image_client = compute_v1.ImagesClient()
        family_name = f"{self.family}{self.release}"
        newest_image = image_client.get_from_family(project=self.image_project,
                                                    family=family_name)
        info_message = f"Newest image is {newest_image.name}"
        self.logger.info(info_message)

        return newest_image.name

    def wait_for_extended_operation(self,
                                    operation: ExtendedOperation,
                                    verbose_name: str = "operation",
                                    timeout: int = 300):
        """
        Waits for the extended (long-running) operation to complete.

        If the operation is successful, it will return its result.
        If the operation ends with an error, an exception will be raised.
        If there were any warnings during the execution of the operation
        they will be printed to sys.stderr.

        Args:
            operation: a long-running operation you want to wait on.
            verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
            timeout: how long (in seconds) to wait for operation to finish.
                If None, wait indefinitely.

        Returns:
            Whatever the operation.result() returns.

        Raises:
            This method will raise the exception received from `operation.exception()`
            or RuntimeError if there is no exception set, but there is an `error_code`
            set for the `operation`.

            In case of an operation taking longer than `timeout` seconds to complete,
            a `concurrent.futures.TimeoutError` will be raised.
        """
        result = operation.result(timeout=timeout)

        if operation.error_code:
            error_message = \
                f"Error during {verbose_name}: [Code: {operation.error_code}]: " \
                f"{operation.error_message}"
            self.logger.error(error_message)
            error_message = f"Operation ID: {operation.name}"
            self.logger.error(error_message)
            raise operation.exception() or RuntimeError(operation.error_message)

        if operation.warnings:
            error_message = f"Warnings during {verbose_name}:\n"
            self.logger.error(error_message)
            for warning in operation.warnings:
                self.logger.error(f" - {warning.code}: {warning.message}")

        return result

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def run_instance(self):
        """
        Method for running GCP instance.
        """
        compute_client = compute_v1.InstancesClient()
        image_name = self.get_image_from_family()
        # Create request body for instance
        instance_config = {
            "name": self.instance_name,
            "machine_type": f"zones/{self.zone}/machineTypes/n1-standard-1",
            "metadata": {
                "items": [
                    {
                        "key": "ssh-keys",
                        "value": f"{config.instance_user}:{config.instance_public_key}"
                    }
                ]
            },
            "disks": [
                {
                    "boot": True,
                    "initialize_params": {
                        "source_image":
                            f"projects/{self.image_project}/global/images/{image_name}"
                    },
                }
            ],
            "network_interfaces": [
                {
                    "access_configs": [
                        {
                            "name": "External NAT",
                            "network_tier": "PREMIUM"
                        }
                    ],
                    "stack_type": "IPV4_ONLY",
                    "subnetwork": self.subnetwork
                }
            ],
        }

        # Create request
        request = compute_v1.InsertInstanceRequest()
        request.zone = self.zone
        request.project = self.project_id
        request.instance_resource = instance_config

        try:
            operation = compute_client.insert(request=request)
            self.wait_for_extended_operation(operation, "instance creation")
            # service pause
            time.sleep(10)
            info_message = f"Instance {self.instance_name} created."
            self.logger.info(info_message)
        except Exception as e:
            self.terminate()
            error_message = f"Instance {self.instance_name} exists. Deleting..."
            self.logger.error(error_message)
            # service pause
            time.sleep(60)
            raise e

    def instance_ip(self):
        """
        Method for return GCP instance ip address.

        return: str
        """
        # Create GCP client
        credentials = \
            service_account.Credentials.from_service_account_file(credentials_path)
        compute_client = discovery.build('compute', 'v1', credentials=credentials)
        instance = compute_client.instances().get(project=self.project_id,
                                                  zone=self.zone,
                                                  instance=self.instance_name).execute()
        instance_ip = instance["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
        # Logger message
        info_message = f"Instance {self.instance_name} ip address = {instance_ip}"
        self.logger.info(info_message)

        return instance_ip

    def terminate(self):
        """
        Method for delete GCP instance.

        return: dict
        """
        # Create GCP client
        credentials = \
            service_account.Credentials.from_service_account_file(credentials_path)
        compute_client = discovery.build('compute', 'v1', credentials=credentials)
        request = compute_client.instances().delete(project=self.project_id,
                                                    zone=self.zone,
                                                    instance=self.instance_name)
        response = request.execute()
        # Logger message
        info_message = f"Instance {self.instance_name} deleted."
        self.logger.info(info_message)

        return response
