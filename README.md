Basic pythonic implementation for querying the FireEye Intelligence api for mass data acquisition for localized parsing.\
Default implementation pulls the last 90 days of IOC and Reports.

## Leverages:

  [FireEye Intel APIv3](https://api.intelligence.fireeye.com/docs#introduction-intel-apiv3)

## Requires:
  Python3.9 or newer\
  [pandas-1.3.3](https://pandas.pydata.org/pandas-docs/stable/whatsnew/index.html)
  
`pip install pandas`

## Usage:
Add required variables to your .env file.\
The APP_NAME variable is used to identify Api activety by FireEye.
```
PUB=FireEyePublicKeyHere
PRIV=FireEyePrivateKeyHere
OUTPATH=/Path/To/Output/Here/
APP_NAME=OrganizationalNameHere
```
Execute the python file FirePy.py

`python3 FirePy.py`

Output will be directed to the path declared in your .env file, seperated by asset leveraged, and saved to a csv file with todays date as it's name.


## Limitations:

50,000 queries per day, 1000 queries per second. Reference comments in the python file for individual endpoint limitations. All lengths are set to the maximum by default.

## Run as a compiled exe for immutability.

Requires:
[pyinstaller](https://pyinstaller.readthedocs.io/en/stable/)\
Packages all dependencies and libraries into a single exe.

```
pip install pyinstaller
pyinstaller -F --paths=<your_path>\Lib\site-packages FirePy.py
```
