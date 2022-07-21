# Installing TimescaleDB
Before you begin installing TimescaleDB, make sure you have installed PostgreSQL
version 12 or later.

## Windows Installation
Full installation instructions can be found [here](https://docs.timescale.com/install/latest/self-hosted/installation-windows/).


## Debian/Ubuntu Installation
Full installation instructions can be found [here](https://docs.timescale.com/install/latest/self-hosted/installation-debian/).


## Raspberry Pi OS Installation
To install TimescaleDB on Raspberry Pi OS, it must be built from source. It will
require CMake version 3.11 or later and a C language compiler, such as gcc or clang, gcc should have already been installed during OS installation.

### Installing CMake
To install CMake, first find the link to download the latest release Unix/Linux
source distribution [here](https://cmake.org/download/). In this example, the
latest release is 3.23.0, with the source distribution filename
'cmake-3.23.0.tar.gz'. Once you have found the source distribution, run:
```shell
sudo apt install build-essential libssl-dev
wget https://github.com/Kitware/CMake/releases/download/v3.23.0/cmake-3.23.0.tar.gz
tar -zxvf cmake-3.23.0.tar.gz
cd cmake-3.23.0
./bootstrap
make
sudo make install
```

### Installing TimescaleDB From Source
Instructions to install TimescaleDB from source and configure PostgreSQL can
be found [here](https://docs.timescale.com/install/latest/self-hosted/installation-source/).

PostgreSQL server development files are required to install TimscaleDB, if you
are having trouble with installation, ensure you've got them installed by
running:
```
sudo apt-get install postgresql-server-dev-12
```
Replacing '12' with your currently installed PostgreSQL version.


# Setting up the TimescaleDB extension
Once TimescaleDB is installed on your version of PostgreSQL, connect to the
PostgreSQL instance with `psql`, connect to your desired database with
`\c DATABASE_NAME` and add the TimescaleDB extension
with:
```pgsql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

When intialising the database with [db/init.sql](../db/init.sql), this step
is completed for you.
