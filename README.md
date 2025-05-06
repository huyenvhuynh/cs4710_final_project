# cs4710_final_project

### Install python:
sudo apt update

sudo apt-get install python3

### Create/activate virtual environment:
python3 -m venv venv

source venv/bin/activate

### Run:
sudo apt-get install sumo sumo-tools sumo-doc

pip install matplotlib

pip install pandas

pip install numpy

python test_visualization.py

### If you're getting "E: Unable to locate package sumo-gui":
sudo apt install software-properties-common

sudo add-apt-repository ppa:sumo/stable

sudo apt update

sudo apt install git cmake g++ libxerces-c-dev libfox-1.6-dev libgdal-dev libproj-dev libgl2ps-dev libfftw3-dev libeigen3-dev libtiff-dev libpng-dev libgl-dev libglu1-mesa-dev libtool swig python3 python3-dev python3-pip

git clone https://github.com/eclipse/sumo.git

cd sumo

mkdir build && cd build

cmake ..

make -j$(nproc)

### Run GUI:
./bin/sumo-gui -c your_config.sumocfg
