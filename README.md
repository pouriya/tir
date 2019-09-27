# `tir`
Have [**time.ir**](http://time.ir) in shell!


![tir-screenshot](https://user-images.githubusercontent.com/20663776/48029334-dbb70d80-e145-11e8-86ce-20746f1d89d2.png)


## Installation
#### Download
Using `git`:  
```sh
~ $ git clone --depth 1 --branch 19.09.21 https://github.com/Pouriya-Jahanbakhsh/tir && cd tir
~/tir $
```
Using `wget`:  
```sh
~ $ wget https://github.com/Pouriya-Jahanbakhsh/tir/archive/19.09.21.tar.gz && tar xf 19.09.21.tar.gz && cd tir-19.09.21
~/tir-19.09.21 $
```

#### Dependencies
First you need to have **Python 3.^5** installed. Most of other dependencies are by default installed on most Linuxes.  
* **setuptools**  
    On most linux distributions:  
    ```sh
    ~ $ sudo apt install python3-setuptools
    ```  
    On FreeBSD:  
    ```sh
    ~ # pkg install py36-setuptools
    ```
* **requests**  
    On most linux distributions:  
    ```sh
    ~ $ sudo apt install python3-requests
    ```  
    On FreeBSD:  
    ```sh
    ~ # pkg install py36-requests
    ```  
* **lxml**  
    On most linux distributions:  
    ```sh
    ~ $ sudo apt install python3-lxml
    ```  
    On FreeBSD:  
    ```sh
    ~ # pkg install py36-lxml
    ```  
    Note that `lxml` itself needs `libxml2` and `libxslt` to compile.

Note that on `FreeBSD` it's better to link your `python3.*` to `python3`:
```sh
~ # ln -s /usr/local/bin/python3.6 /usr/local/bin/python3
```
Or edit `Makefile` and first line of `./bin/crawler.py` and place your own Python 3 command

  #### Notification is not show for you?
  just run this command to reinstall or install libraries to solve the problem:
  ```
  ~ $ sudo apt-get --reinstall install libnotify-bin notify-osd
  ```
  
#### install `tir` itself
On Linux distributions run:
```sh
~/path/to/tir $ sudo make install
```  
On `FreeBSD` you need `gmake` instead of `make`:
```sh
~/path/to/tir # gmake install
```  

Then you have `tir` command everywhere:
```text
/x/y/z $ tir
Emruz: 3-Shanbeh  15   Aban(08)   1397   Pa'eez  
Today:  Tuesday   06 November(11) 2018   Autumn  
System time: 00:04:03
 ________  ________  ________  ________  ________  ________  ________
| Shanbe ||  Yek   ||   Do   ||   Se   || Chahar ||  Panj  || Jom'eh |
 ________  ________  ________  ________  ________  ________  ________ 
|        ||        ||        ||        ||        ||        ||        |
|   28   ||   29   ||   30   ||   01   ||   02   ||   03   ||   04   |
| 10  20 || 11  21 || 12  22 || 13  23 || 14  24 || 15  25 || 16  26 |
|________||________||________||________||________||________||________|
 ________  ________  ________  ________  ________  ________  ________ 
|        ||        ||        ||        ||        ||        ||        |
|   05   ||   06   ||   07   ||   08   ||   09   ||   10   ||   11   |
| 17  27 || 18  28 || 19  29 || 20  30 || 21  31 || 22  01 || 23  02 |
|________||________||________||________||________||________||________|
 ________  ________  ________  ________  ________  ________  ________ 
|        ||        ||        ||        ||        ||        ||        |
|   12   ||   13   ||   14   ||   15   ||   16   ||   17   ||   18   |
| 24  03 || 25  04 || 26  05 || 27  06 || 28  07 || 29  08 || 01  09 |
|________||________||________||________||________||________||________|
 ________  ________  ________  ________  ________  ________  ________ 
|        ||        ||        ||        ||        ||        ||        |
|   19   ||   20   ||   21   ||   22   ||   23   ||   24   ||   25   |
| 02  10 || 03  11 || 04  12 || 05  13 || 06  14 || 07  15 || 08  16 |
|________||________||________||________||________||________||________|
 ________  ________  ________  ________  ________  ________  ________ 
|        ||        ||        ||        ||        ||        ||        |
|   26   ||   27   ||   28   ||   29   ||   30   ||   01   ||   02   |
| 09  17 || 10  18 || 11  19 || 12  20 || 13  21 || 14  22 || 15  23 |
|________||________||________||________||________||________||________|

Powered by http://time.ir
```

## Uninstallation
On Linux distributions run:
```sh
~/path/to/tir $ sudo make uninstall
```  
On `FreeBSD` you need `gmake` instead of `make`:
```sh
~/path/to/tir # gmake uninstall
```  

## Arguments
```sh
root@codefather:~/tir $ tir -h
```
```text
Usage: tir [options]

Options:
  -h, --help       show this help message and exit
  -s, --solar      Does not show solar date
  -g, --gregorian  Does not show gregorian date
  -c, --calendar   Does not show calendar
  -t, --time       Does not show time
  -C, --color      Does not show colored text
  -q, --quote      Does not notify for quote
  -H, --holidays   Does not notify for holidays
  -a, --about      shows program's description and exits
```
So for example `tir -s -g -c -C -q -H` will result:
```sh
Emruz: 3-Shanbeh  15   Aban(08)   1397   Pa'eez  

Powered by http://time.ir
```

# Contributing
I love pull requests from everyone ! For more info see `CONTRIBUTING.md` file.
