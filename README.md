## vmmetadata: vCenter metadata (custom fields) export/import tool 

This command-line tool lets you export/import metadata (custom fields) from/to a VMWare vCenter host.

Requirements
* linux or windows box
* Python 2.6 or higher
* [argparse](https://docs.python.org/3/library/argparse.html) library
* [pyvmomi](https://github.com/vmware/pyvmomi) library
* [pyyaml](http://pyyaml.org/) library
* access to a VMWare vCenter host

Installation:
-------------
* Clone repository   
`git clone https://github.com/sebbrochet/vmmetadata.git`
* cd into project directory   
`cd vmmetadata`
* Install requirements with pip   
`pip install -r requirements.txt`
* Install vmmetadata binary   
`python setup.py install`

Usage:
------

```
usage: vmmetadata [-h] [-m METADATAFILE] [-s SCOPE] [-u USER] [-p PASSWORD]
                  [-t TARGET] [-o PORT] [-d DATACENTER] [-c CONFIG] [-v]
                  command

vCenter metadata (custom fields) export/import tool.

positional arguments:
  command               Command to execute (export, import, list)

optional arguments:
  -h, --help            show this help message and exit
  -m METADATAFILE, --metadatafile METADATAFILE
                        Name of the metadata file to use for export/import
  -s SCOPE, --scope SCOPE
                        Limit command to act on scope defined in a file
  -u USER, --user USER  Specify the user account to use to connect to vCenter
  -p PASSWORD, --password PASSWORD
                        Specify the password associated with the user account
  -t TARGET, --target TARGET
                        Specify the vCenter host to connect to
  -o PORT, --port PORT  Port to connect on (default is 443)
  -d DATACENTER, --datacenter DATACENTER
                        Specify the datacenter name to run commands on
                        (default is all datacenters)
  -c CONFIG, --config CONFIG
                        Configuration file to use
  -v, --version         Print program version and exit.
```

`scope` of VM to be listed/exported/imported can be defined in a file by listing the short VM names, one by line.   
A line starting with a `#` is considered as comment and won't be interpreted.     

`config` format is one argument by line (i.e argname=value), argument names are the same ones than the CLI (scope, user, password, ...).   
A line starting with a `#` is considered as comment and won't be interpreted.    
Don't put quotes between argument values
