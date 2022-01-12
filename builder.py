import subprocess
import os
from setuptools import Extension
from setuptools.command.build_ext import build_ext

from setuptools.command.build_py import build_py


class CryptoExtension(Extension):
    def __init__(self):
        self.name = "crypto_cpp"
        Extension.__init__(self, self.name, sources=[])


class BuildPy(build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()


class BuildCrypto(build_ext):
    already_built = False

    def build_extension(self, ext):
        if self.already_built:
            print("was already built, skipping...")
            return

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

        self.already_built = True
