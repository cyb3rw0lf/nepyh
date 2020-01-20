# N.E.Py.H. - Network Engineer Python Helper

## NEPYH-BIN (Windows only)
Download the binary file:
https://github.com/cyb3rw0lf/nepyh-bin/nepyh-bin.exe

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

### Run Software
python3 nepyh.py


## NEPYH-CLI
### Installation
Download the repo
```
git clone https://github.com/cyb3rw0lf/nepyh-cli
```

Enter the downloaded folder
```
cd nepyh-cli
```

Install dependencies
```
pip3 install -r requirements.txt
```

### Upgrade
Enter the downloaded folder
```
cd nepyh-cli
```

Pull the repo
```
git pull
```

### Run Software
```
python3 nepyh-cli.py -t <template_file>.j2 -d <db_file>.yml -p <project_folder> -e <output_file_extension>
```

```
-h|--help This help menu
 -e File Extension for output file, default .txt
 -t Template file in Jinja2 format .j2
 -d DB file in YAML format .yml
 -p Project Folder for output files, default "%Y%m%d-%H%M%S"
```
