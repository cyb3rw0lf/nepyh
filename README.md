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

### Jinj2 Custom Filters
The Jinja2 template support the following custom filters for IP Address management

```ip``` return IP Address as string
```ipadd``` return IP Address + the amount of IP Added as string
```network``` return the Network Address as string
```broadcast``` return the Wildcard Mask as string
```bitmask``` return the Bit Mask / Prefix lenght as string
```netmask``` return Subnet Mask as string
```wildmask``` return the Wildcard Mask as string

Usage:
```YAML
---
my_ipv4: 192.168.100.1/24
my_ipv6: 2001:db8::85a3:7334/64
```

```Jinja2
IPV4:
IP Address: {{ my_ipv4|ip }}
 Result: 192.168.100.1
Add 5 IP Address: {{ my_ipv4|ipadd(5) }}
 Result: 192.168.100.6
Network Address: {{ my_ipv4|network }}
 Result: 192.168.100.0
Broadcast Address: {{ my_ipv4|broadcast }}
 Result: 192.168.100.255
Bit Mask: {{ my_ipv4|bitmask }}
 Result: 24
Subnet Mask: {{ my_ipv4|netmask }}
 Result: 255.255.255.0
Wildcard Mask: {{ my_ipv4|wildmask }}
 Result: 0.0.0.255

IPV6:
IP Address: {{ my_ipv6|ip }}
 Result: 2001:db8::85a3:7334
Add 5 IP Address: {{ my_ipv6|ipadd(5) }}
 Result: 2001:db8::85a3:7339
Network Address: {{ my_ipv6|network }}
 Result: 2001:db8::
Broadcast Address: {{ my_ipv6|broadcast }}
 Result: 2001:db8::ffff:ffff:ffff:ffff
Bit Mask: {{ my_ipv6|netmask }}
 Result: 64
Subnet Mask: {{ my_ipv6|bitmask }}
 Result: ffff:ffff:ffff:ffff::
Wildcard Mask: {{ my_ipv6|wildmask }}
 Result: ::ffff:ffff:ffff:ffff
```


## NEPYH-BIN (Windows only)
Download the binary file:
https://github.com/cyb3rw0lf/nepyh/releases/latest


## NEPYH-CLI
Command line version available here: https://github.com/cyb3rw0lf/nepyh-cli

