# MetaReserve-GENI
[MetaReserve](https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve) plugin for GENI resources.

## Requirements
 - Python >= 3.2 `AND` Python 2.7
 - [MetaReserve](https://github.com/Sebastiaan-Alvarez-Rodriguez/metareserve) >= 0.1.0

Additionally, for python2.7, the following packages are needed:
 - `lxml`
 - `six`
 - `geni-lib==0.9.9.2`


## Installing
Simply run `pip3 install metareserve-GENI --user`.


## Usage
With this package, a new command `geni-reserve` will be available.
It can doe 3 things:
 - `list` slices & allocated resources for a given slice.
 - `allocate` resources on a cluster site. Users can specify the hostname, hardware type and image to boot per node. Configurations can be saved an reused.
 - `deallocate` resources.
Use `geni-reserve -h` for more information.