# OSM Route Compare

Extract OSM road-routes from regional extracts with their member ways for analysis.

This package utilizes the msgpack intermediary format to allow chaining of actions
and processing a stream of results one by one. For comparing algorithms or rerunning
later actions it can be useful to write the intermediary results to disk for reuse.
Alternatively, results can be piped on STDOUT/STDIN to the next command.

## Installation

### Prerequisites

*Python*
This is a Python script, therefore you need a functional Python 3 or later environment on your computer.
This program has been tested on Python 3.5.
See http://python.org/

*Boost.Python*
Boost is system for providing C++ libraries (like libosmium) to Python

*libosmium*
http://osmcode.org/libosmium/manual.html#building-libosmium

The `sparsehash` package will also be needed for the following to work.

    wget https://github.com/osmcode/libosmium/archive/v2.10.2.tar.gz
    tar xzf v2.10.2.tar.gz
    cd  libosmium-2.10.2/
    mkdir build
    cd build
    cmake -g INSTALL_PROTOZERO ../
    make && make install


*pyosmium*
After libosmium is available on your system, you should be able to use `pip` to
install the python osmium bindings.

    pip install osmium

Issues: On my system (OS X 10.10.5 with most packages installed via MacPorts) I
had to take two additional steps to fix errors in building osmium with `pip`.

1. MacPorts put the boost.python installation in `/opt/local/include/boost/` while
   osmium is looking for it in `/opt/local/lib/boost/`. Making a symbolic link
   solved this.

        cd /opt/local/lib
        ln -s ../include/boost boost

2. I was seeing the following error:

        In file included from lib/osmium.cc:5:
        In file included from /usr/local/include/osmium/area/assembler.hpp:62:
        /usr/local/include/osmium/tags/filter.hpp:41:10: fatal error: 'boost/iterator/filter_iterator.hpp' file not found
        #include <boost/iterator/filter_iterator.hpp>

I fixed this by ensuring that a `BOOST_PREFIX` variable was in my shell environment
before running `pip`:

        export BOOST_PREFIX=/opt/local/
        pip install osmium

*msgpack*
curvature makes use of `msgpack` which you can find at
[python.org](https://pypi.python.org/pypi/msgpack-python) and installed
with `pip` or `easy_install`:

    pip install msgpack-python

### Preparation

Once your Python environment set up and the `imposm.parser` and `msgpack-python` modules are installed, just download
this package and run one of the example commands below from its directory.

    git clone https://github.com/adamfranco/osm-route-compare.git
    cd osm-route-compare

## Usage

Extract each route in an OSM PBF file and attach its member ways (with tags) under a 'ways' key:

    bin/osm-route-collect -v --highway_types 'motorway,trunk,primary,secondary,tertiary,unclassified,residential,service,motorway_link,trunk_link,primary_link,secondary_link' vermont.osm.pbf > vermont-routes.msgpack

Inspect the data with the msgpack-reader:

    cat vermont-routes.msgpack | msgpack-reader

Check for redundant_names and annotate with name_is_redundant flags, then output as a tab-delimited file:

    cat vermont-routes.msgpack | bin/osm-route-analyze flag_redundant_way_names_simple | bin/osm-route-output-tab > vermont-routes.txt
