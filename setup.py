
import io
import re
import setuptools
import sys

with io.open('src/pliz/__init__.py', encoding='utf8') as fp:
  version = re.search(r"__version__\s*=\s*'(.*)'", fp.read()).group(1)

with io.open('README.md', encoding='utf8') as fp:
  long_description = fp.read()

requirements = ['contexter >=0.1.4,<0.2.0', 'nr.databind >=0.9.0.dev0,<1.0.0', 'requests >=2.22.0,<3.0.0', 'PyYAML >=5.1.0,<6.0.0', 'termcolor >=1.1.0,<2.0.0']

setuptools.setup(
  name = 'pliz',
  version = version,
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  description = 'Automates the heavy lifting of release and distribution management for pure Python packages.',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = 'https://git.niklasrosenstein.com/NiklasRosenstein/pliz',
  license = 'MIT',
  packages = setuptools.find_packages('src'),
  package_dir = {'': 'src'},
  include_package_data = False,
  install_requires = requirements,
  tests_require = [],
  python_requires = None, # TODO: '>=2.7,<3.0.0|>=3.4,<4.0.0',
  entry_points = {
    "console_scripts": [
      "pliz = pliz.__main__:console_main"
    ]
  }
)
