import os
import subprocess
from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CryptoExtension(Extension):
    def __init__(self):
        self.name = "crypto_cpp"
        Extension.__init__(self, self.name, sources=[])


class BuildCrypto(build_ext):
    def build_extension(self, ext):
        # TODO: Check if windows and then execute corresponding script
        subprocess.run("chmod +x ./build_extension.sh", shell=True, check=True)
        subprocess.run(
            "./build_extension.sh",
            shell=True,
            check=True,
        )
