# South African Domestic Load Research Data Explorer

## 1. Installation Instructions

### Install required software
1. Download Python via Anaconda: https://www.anaconda.com/download/
2. [Install](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup) git. 

#### A) Install the application
[Clone](https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository) this repository with git.

#### B) Install pip
Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) to a folder on your computer. Open the Anaconda prompt (Windows), terminal window (Mac) or bash (Linux) and navigate to the folder containing get-pip.py. Then run `python get-pip.py`. This will install pip.

#### C) Install pre-requisite packages
Copy and paste the following into the Anaconda prompt/terminal/bash, and hit enter. You must have an internet connection for this to work.
```
conda install -c conda-forge feather-format
conda install -c conda-forge dash 
conda install -c conda-forge dash-renderer
conda install -c conda-forge dash-html-components
conda install -c conda-forge dash-core-components
pip install ckanapi
```
## 2. Request Data Access
#### A) Get data API-key
A. Create your user profile on the [Energy Research Data Portal for South Africa](http://energydata.uct.ac.za).
2. Submit a [data access request form](https://goo.gl/forms/iRfplqQfzc7mEczs2) providing your details. You will receive a response within a week whether your request has been granted.
3. Navigate to your user profile at http://energydata.uct.ac.za/user/USERNAME and copy the API-key at the bottom of the left sidebar.

## 3. Run the app
1. Open the app.py file in the DLR_app directory with spyder (python development environment that comes with Anaconda). You can find spyder by typing 'spyder' into your computer's search.
2. Run app.py (ie click on the green triangle that is the 6th icon in the toolbar at the top of spyder).
3. Open **127.0.0.1:8050** in your browser bar to view the app. 
4. Wait a minute or two for the app to load.
5. Happy data play!
