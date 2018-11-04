# `tir`
Have [**time.ir**](time.ir) in shell!


![tir-screenshot]()


## Installation

#### Dependencies
First you need to have **Python 3.^5** installed. Most of other dependencies are by default installed on most Linuxes.  
* **setuptools**
    ```sh
    ~ $ [sudo] pip --disable-pip-version-check setuptools
    ```  
* **requests**
    ```sh
    ~ $ [sudo] pip --disable-pip-version-check requests
    ```  
* **lxml**
    `lxml` needs packages `libxml2` and `libxslt` installed
    ```sh
    ~ $ [sudo] pip --disable-pip-version-check lxml
    ```  

### tir
```sh
~/path/to/tir $ [sudo] make install
```  
Then you have to have `tir` command everywhere:
```sh
/x/y/z $ tir
Emruz: 1-Shanbeh  13   Aban(08)   1397   Pa'eez  
Today:   Sunday   04 November(11) 2018   Autumn  
System time: 20:30:16
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
```

## Uninstallation
```sh
~/path/to/tir $ [sudo] make uninstall
```  

## Arguments
root@codefather:~/tir # tir -h
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
```
So for example `tir -s -g -c -C -q -H` will result:
```sh
Emruz: 1-Shanbeh  13   Aban(08)   1397   Pa'eez
```

