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
# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starknet_py',
 'starknet_py.cairo',
 'starknet_py.net',
 'starknet_py.net.account',
 'starknet_py.net.l1',
 'starknet_py.net.models',
 'starknet_py.utils',
 'starknet_py.utils.compiler',
 'starknet_py.utils.crypto',
 'starknet_py.utils.data_transformer',
 'starknet_py.utils.sync']

package_data = \
{'': ['*']}

install_requires = \
['asgiref>=3.4.1,<4.0.0',
 'cairo-lang==0.8.1',
 'typing-extensions<4',
 'web3>=5.28.0,<6']

extras_require = \
{'docs': ['sphinx>=4.3.1,<5.0.0', 'enum-tools[sphinx]==0.9.0']}

setup_kwargs = {
    'name': 'starknet.py',
    'version': '0.2.2a0',
    'description': 'A python SDK for StarkNet',
    'long_description': '<div align="center">\n    <img src="https://raw.githubusercontent.com/software-mansion/starknet.py/master/graphic.png" alt="starknet.py"/>\n</div>\n<h2 align="center">StarkNet SDK for Python</h2>\n\n<p align="center">\n\n[![codecov](https://codecov.io/gh/software-mansion/starknet.py/branch/master/graph/badge.svg?token=3E54E8RYSL)](https://codecov.io/gh/software-mansion/starknet.py)\n[![pypi](https://img.shields.io/pypi/v/starknet.py)](https://pypi.org/project/starknet.py/)\n[![build](https://img.shields.io/github/workflow/status/software-mansion/starknet.py/format%20-%3E%20lint%20-%3E%20test)](https://github.com/software-mansion/starknet.py/actions)\n[![docs](https://readthedocs.org/projects/starknetpy/badge/?version=latest)](https://starknetpy.readthedocs.io/en/latest/?badge=latest)\n[![license](https://img.shields.io/badge/license-MIT-black)](https://github.com/software-mansion/starknet.py/blob/master/LICENSE.txt)\n[![stars](https://img.shields.io/github/stars/software-mansion/starknet.py?color=yellow)](https://github.com/software-mansion/starknet.py/stargazers)\n[![starkware](https://img.shields.io/badge/powered_by-StarkWare-navy)](https://starkware.co)\n\n</p>\n\n## 📘 Documentation\n- [Installation](https://starknetpy.rtfd.io/en/latest/installation.html)\n- [Quickstart](https://starknetpy.rtfd.io/en/latest/quickstart.html)\n- [Guide](https://starknetpy.rtfd.io/en/latest/guide.html)\n- [API](https://starknetpy.rtfd.io/en/latest/api.html)\n\n## Installation\nTo install this package run\n\n`pip install starknet.py`\n\nor using Poetry:\n\n`poetry add starknet.py`\n\n## ▶️ Example usage\n### Asynchronous API\nThis is the recommended way of using the SDK.\n```\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.client import Client\n\nkey = 1234\ncontract = await Contract.from_address("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))\ninvocation = await contract.functions["set_value"].invoke(key, 7)\nawait invocation.wait_for_acceptance()\n\n(saved,) = await contract.functions["get_value"].call(key) # (7)\n```\n\n### Synchronous API\nYou can access synchronous world with `_sync` postfix.\n\n```\nfrom starknet_py.contract import Contract\nfrom starknet_py.net.client import Client\n\nkey = 1234\ncontract = Contract.from_address_sync("0x01336fa7c870a7403aced14dda865b75f29113230ed84e3a661f7af70fe83e7b", Client("testnet"))\ninvocation = contract.functions["set_value"].invoke_sync(key, 7)\ninvocation.wait_for_acceptance_sync()\n\n(saved,) = contract.functions["get_value"].call_sync(key) # 7\n```\n\nSee more [here](https://starknetpy.rtfd.io/en/latest/quickstart.html).',
    'author': 'Tomasz Rejowski',
    'author_email': 'tomasz.rejowski@swmansion.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/software-mansion/starknet.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.2,<3.10',
}


setup(**setup_kwargs)

# This setup.py was autogenerated using poetry.
