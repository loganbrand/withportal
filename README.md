# South African Domestic Load Research Data Explorer

## Installation Instructions

### Install required software
1. Download Python via Anaconda: https://www.anaconda.com/download/
2. [Install](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) git. 

#### Install the application
[Clone](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) this repository with git.

#### Install pip
Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) to a folder on your computer. Open a command (cmd) prompt window (go to Windows search bar and search for cmd), terminal window (Mac search terminal) or bash (Linux) and navigate to the folder containing get-pip.py. Then run `python get-pip.py`. This will install pip.

#### Install pre-requisite packages
In the cmd/terminal/bash execute the following commands:
```
pip install feather-format
pip install ckanapi
```
## Request Data Access
#### Get data API-key
1. Create your user profile on the [Energy Research Data Portal for South Africa](http://energydata.uct.ac.za).
2. Submit a [data access request form](https://goo.gl/forms/iRfplqQfzc7mEczs2) providing your details. You will receive a response within a week whether your request has been granted.
3. Navigate to your user profile at http://energydata.uct.ac.za/user/USERNAME and copy the API-key at the bottom of the left sidebar.

## Run the app
1. Open the app.py file in the DLR_app directory with spyder (python development environment that comes with Anaconda).
2. Run the file.
3. Navigate to 127.0.0.1:8050 to view the app.
4. Happy data play!
