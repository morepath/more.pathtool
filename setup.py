import io
from setuptools import setup, find_packages

long_description = (
    io.open('README.rst', encoding='utf-8').read()
    + '\n' +
    io.open('CHANGES.txt', encoding='utf-8').read())

setup(name='more.pathtool',
      version='0.1.dev0',
      description="Information about path configuration in Morepath",
      long_description=long_description,
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      keywords='morepath',
      license="BSD",
      url="http://pypi.python.org/pypi/more.pathinfo",
      namespace_packages=['more'],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'morepath >= 0.15',
          'dectate',
      ],
      extras_require=dict(
          test=[
              'pytest >= 2.9.0',
              'pytest-remove-stale-bytecode',
          ],
          coverage=[
              'pytest-cov',
          ],
          pep8=[
              'flake8',
          ],
          docs=[
              'sphinx',
          ],
      ))
