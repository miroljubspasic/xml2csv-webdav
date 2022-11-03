from setuptools import setup

setup(
    name="xml2csv",
    version="1.0",
    description='Convert .customers xml into .csv file',
    py_modules=["custom"],
    include_package_data=True,
    install_requires=["webdav4", "xmltodict", "python-dotenv"],
    entry_points="""
        [console_scripts]
        xml2csv=main:main
    """,

)