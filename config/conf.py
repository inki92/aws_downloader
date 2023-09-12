"""Replace these values with your credentials"""

# AWS creds
aws_access_key_id = '<key_id>'
aws_secret_access_key = '<secret_access_key>'
aws_region = '<aws_region>'
aws_token = '<aws_session_token>'
ami_id_9 = '<AMI ID el9>'
ami_id_8 = '<AMI ID el8>'
instance_type = 't2.micro'
key_pair_name = '<key pair name>'
security_group_ids = ['<sg_id_1>', '<sg_id_2>']
instance_mount_dir = "/home/ec2-user/rpm/"
# instance_user = 'ec2-user'
# instance_mount_dir = "/home/ec2-user/rpm/"

# GCP creds
instance_user = '<instance_user>'
instance_public_key = "<ssh_public_key>"
instance_mount_dir = f"/home/{instance_user}/rpm/"
project_id = '<gcp_project_id>'
zone = '<gcp_zone>'
region = '<gcp_region>'
instance_name = '<gcp_instance_name>'
machine_type = 'n1-standard-1'
family = '<gcp_source_image_family>'
project = '<gcp_source_image_project>'
subnetwork = '<gcp_subnetwork_link>'

# Local vars
local_mount_dir = "<local_mount_directory>"
expected_license_hash = '<sha256sum_of_the_license_on_instance>'
private_key_path = '<private_ssh_key_path>'
license_rpm = '<name of the package with license>'
license_path = '<path to the license file on the instance>'





