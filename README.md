# N.E.Py.H. - Network Engineer Python Helper

NEPYH is a python application with GUI which takes as input a database (in YAML format) and a template (in Jinja2 format) and merge them in order to generate configuration for network devices.

It can also be used for other things such as generate SecureCRT sessions files


## NEPYH
### Installation
Download the repo
```
git clone https://github.com/cyb3rw0lf/nepyh.git
```

Enter the downloaded folder
```
cd nepyh
```

Install dependencies
```
pip3 install -r requirements.txt
```

### Upgrade
Enter the downloaded folder
```
cd nepyh
```

Pull the repo
```
git pull
```

### Usage
See the sample folder for examples of input files.
* Create a database file in YAML format (validate on http://www.yamllint.com/)
* Create a template file in Jinja2 format
* Run the software
  * _Linux_ ``` python3 nepyh.py ```
  * _Windows_ ``` py nepyh.py ```
* Select database, template, project name, output extension and press "Run"
  
  ![NEPyH Screenshot](/samples/nepyh_screenshot.png)


### YAML restrictions
The YAML file must start with a list of dictionaries.

The first dictionary will be used as name for the output files.

YAML example:
```YAML
---
- hostname: R1
  loopback: 1.1.1.1
- hostname: R2
  loopback: 2.2.2.2
```

Output example:
```
R1.txt
R2.txt
```

## NEPYH-BIN (Windows only)
Download the binary file:
https://github.com/cyb3rw0lf/nepyh/releases/latest


## NEPYH-CLI
Command line version available here: https://github.com/cyb3rw0lf/nepyh-cli

