import subprocess
import os
from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CryptoExtension(Extension):
    def __init__(self):
        self.name = "crypto_cpp"
        Extension.__init__(self, self.name, sources=[])


class BuildCrypto(build_ext):
    def build_extension(self, ext):
        extension = "ps1"
        if os.name != "nt":
            extension = "sh"
            subprocess.run("chmod +x ./build_extension.sh", shell=True, check=True)

        subprocess.run(
            f"./build_extension.{extension}",
            shell=True,
            check=True,
        )
