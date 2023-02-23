from setuptools import find_packages, setup

about = {}
with open("mock_op/__about__.py") as fp:
    exec(fp.read(), about)

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(name='mock-op',
      version=about["__version__"],
      description=about["__summary__"],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Zachary Cutlip",
      author_email="uid000@gmail.com",
      url="TBD",
      license="MIT",
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'mock-op=mock_op.mock_op_main:main',
              'list-cmds=mock_op.list_cmd_main:main',
              'response-generator=mock_op.response_gen_main:main'], },
      python_requires='>=3.7',
      install_requires=['mock-cli-framework>=0.3.1'],
      package_data={'mock_op': ['config/*']},
      )
