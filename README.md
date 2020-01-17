# N.E.Py.H. - Network Engineer Python Helper

## NEPYH-BIN (Windows only)
Download the binary file:
https://github.com/cyb3rw0lf/nepyh/bin

## NEPYH-GUI
### Installation
Download the repo
```
git clone https://github.com/cyb3rw0lf/nepyh/gui nepyh-gui
```

Enter the downloaded folder
```
cd nepyh-gui
```

Install dependencies
```
pip3 install -r requirements.txt
```

### Upgrade
Enter the downloaded folder
```
cd nepyh-gui
```

Pull the repo
```
git pull
```

### Run Software
python3 nepyh-gui.py


## NEPYH-CLI
### Installation
Download the repo
```
git clone https://github.com/cyb3rw0lf/nepyh/cli nepyh-cli
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
