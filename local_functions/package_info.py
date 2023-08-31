"""Module for get metadata from software package."""

import os
import shutil
import glob
import hashlib
import subprocess
import tempfile


class PackageInfo:
    """Class for run query requests to rpm package."""

    def __init__(self, logger, package_path):
        self.package_path = package_path
        self.logger = logger

    def get_rpm_metadata(self):
        """
        Method for get metadata from rpm package.

        :return (str)
        """
        try:
            query = subprocess.run(
                [
                    "rpm",
                    "--nosignature",
                    "-qp",
                    "--queryformat",
                    "Name: %{NAME}\n"
                    "Version: %{VERSION}\n"
                    "Release: %{RELEASE}\n"
                    "Summary: %{SUMMARY}\n"
                    "License: %{LICENSE}\n",
                    self.package_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return query.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error querying RPM file: {e}")

    def get_rpm_content(self):
        """
        Method for get content sha256sums of the rpm package.

        :return: list[str] = []
        """
        results = []
        try:
            # Create temporary directory.
            temp_dir = tempfile.mkdtemp()
            # Extract contents of src.rpm
            cpio_file = os.path.join(temp_dir, "files.cpio")
            with open(cpio_file, "wb") as f:
                subprocess.run(["rpm2cpio", self.package_path],
                               check=True, stdout=f)

            # Unpack cpio archive to temp directory.
            unpack_dir = os.path.join(temp_dir, "unpacked")
            os.makedirs(unpack_dir)
            subprocess.run(["cpio", "-id", "--quiet"], check=True,
                           cwd=unpack_dir, stdin=open(cpio_file, "rb"))

            # Extract gz files.
            gz_files = glob.glob(os.path.join(unpack_dir, "*.gz"))
            for gz_file in gz_files:
                subprocess.run(["gzip", "-d", "-q", gz_file], check=True)
            # Extract bz files.
            bz2_files = glob.glob(os.path.join(unpack_dir, "*.bz2"))
            for bz2_file in bz2_files:
                subprocess.run(["bzip2", "-d", "-q", bz2_file], check=True)

            # Get checksums.
            for root, dirs, files in os.walk(unpack_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_checksum = \
                        hashlib.sha256(open(file_path, "rb").read()).hexdigest()
                    results.append(f'{file}: {file_checksum}')
        finally:
            shutil.rmtree(temp_dir)
        return results

    def get_provides(self):
        """
        Method for get provides section of rpm package.

        :return: (str)
        """
        provides_cmd = [
            "rpm", "--nosignature",
            "-qp", "--provides",
            self.package_path
        ]
        try:
            output = subprocess.check_output(provides_cmd, encoding="utf-8")
            return output.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error querying RPM file: {e}")

    def get_requires(self):
        """
        Method for get requires section of rpm package.

        :return: (str)
        """
        requires_cmd = [
            "rpm",
            "--nosignature",
            "-qp",
            "--requires",
            self.package_path
        ]
        try:
            output = subprocess.check_output(requires_cmd, encoding="utf-8")
            return output.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error querying RPM file: {e}")

    def get_scripts(self):
        """
        Method for get scripts section of rpm package.

        :return: (str)
        """
        scripts_cmd = [
            "rpm",
            "--nosignature",
            "-qp",
            "--scripts",
            self.package_path
        ]
        try:
            output = subprocess.check_output(scripts_cmd, encoding="utf-8")
            return output.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error querying RPM file: {e}")

    def get_files(self):
        """
        Method for get files section of rpm package.

        :return: (str)
        """
        try:
            files_cmd = ["rpm", "-qpl", "--nosignature", self.package_path]
            output = subprocess.check_output(files_cmd, encoding="utf-8")
            return output.splitlines()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error querying RPM file: {e}")

    def get_all(self):
        """
        Method for get all data from rpm package.

        :return: {dict}
        """
        rpm_info = {}
        info = {}
        if self.package_path.endswith(".src.rpm"):
            info["metadata"] = self.get_rpm_metadata()
            info["content"] = self.get_rpm_content()
            info["requires"] = self.get_requires()
            info["provides"] = self.get_provides()
            info["scripts"] = self.get_scripts()
            info["files"] = self.get_files()

        else:
            info["metadata"] = self.get_rpm_metadata()
            info["requires"] = self.get_requires()
            info["provides"] = self.get_provides()
            info["scripts"] = self.get_scripts()
            info["files"] = self.get_files()

        rpm_info[self.package_path] = info
        return rpm_info
