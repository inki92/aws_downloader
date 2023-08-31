"""Replace these values with your AWS credentials"""


class Config:
    def __init__(self):
        self.aws_access_key_id = '<key_id>'
        self.aws_secret_access_key = '<secret_access_key>'
        self.aws_region = 'eu-central-1'
        self.aws_token = '<aws_session_token>'
        self.ami_id_9 = '<AMI ID el9>'
        self.ami_id_8 = '<AMI ID el8>'
        self.instance_type = 't2.micro'
        self.key_pair_name = '<key pair name>'
        self.private_key_path = '<path to key.pem>'
        self.security_group_ids = ['<sg_id_1>', '<sg_id_2>']
        self.expected_license_hash = '<sha256sum of the license on instance>'
        self.local_mount_dir = "<path to local mount point>"
        self.instance_mount_dir = "<path to instance mount point>"
        self.instance_user = 'ec2-user'
        self.license_rpm = '<name of the package with license>'
        self.license_path = '<path to the license file on the instance>'

