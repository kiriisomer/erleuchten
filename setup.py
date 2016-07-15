#!/usr/bin/env python


from setuptools import setup, find_packages

console_entry_points = [
    'erleuchten-testcase=erleuchten.cmd.testcase:main',
    'erleuchten-environment=erleuchten.cmd.environment:main',
    'erleuchten-vm-template=erleuchten.cmd.vm_template:main',
    'erleuchten-vm=erleuchten.cmd.vm:main',
    'erleuchten-script=erleuchten.cmd.script:main',
    'erleuchten-script-set=erleuchten.cmd.script_set:main',
]


setup_requires = ['shutil', ]


setup(name='erleuchten',
      version='0.1',
      description='Test Utilities',
      author='kiriisomer',
      author_email='kiriisomer@hotmail.com',
      url='https://github.com/kiriisomer/erleuchten',
      packages=find_packages(),
      entry_points={'console_scripts': console_entry_points},
      setup_requires=setup_requires
      )
