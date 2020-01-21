# N.E.Py.H. - Network Engineer Python Helper

## NEPYH
### Installation
Download the repo
```
git clone https://github.com/cyb3rw0lf/nepyh
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
* Create a database file in YAML format (validate on http://www.yamllint.com/)
* Create a template file in Jinja2 format
* Run the software ``` python3 nepyh.py ```

### YAML restrictions
The YAML file must start with a list of dictionaries.

The first dictionary will be used as name for the output files.

example:
```YAML
---
- hostname: R1
  loopback: 1.1.1.1
- hostname: R2
  loopback: 2.2.2.2
```

## NEPYH-BIN (Windows only)
Download the binary file:
https://github.com/cyb3rw0lf/nepyh-bin/nepyh-bin.exe


## NEPYH-CLI
Command line version available here: https://github.com/cyb3rw0lf/nepyh-cli

