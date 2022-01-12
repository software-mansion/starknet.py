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
        if os.name != "nt":
            subprocess.run("chmod a+x ./build_extension.sh", shell=True, check=True)
            subprocess.run(
                "./build_extension.sh",
                shell=True,
                check=True,
            )
        else:
            with subprocess.Popen(
                ["powershell.exe", ".\\build_extension.ps1"]
            ) as process:
                process.wait()
                if process.returncode != 0:
                    raise Exception("Build returned a non-zero code")
