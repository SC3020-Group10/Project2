# Project2: Query Analyzer

# Installation
1. Install `PostgreSQL` [here](https://www.postgresql.org/download/)
2. Clone this repository using `git clone https://github.com/SC3020-Group10/Project2.git`
3. Navigate to the root folder of this project
5. Download the TPC-H csv files and sql setup files [here](https://drive.google.com/drive/folders/1sAwyOoHuS35j6GTRL8-COcknz6Lo1S9k?usp=sharing) and place it into the root folder.
6. Create a new python environment using a package manager such as `venv` or `conda` (Note: This project was tested on python 3.11)

**venv**
```
python -m venv myenv
myenv\Scripts\activate
```
**conda**
```
conda create -n myenv python=3.11
conda activate myenv
conda install pip
```
7. Install python dependencies and import the TPC-H dataset into your PostgreSQL database by running `./setup.sh [Your PostgreSQL username] [Your PostgreSQL password]`
8. Start the web application using `./run.sh` or `python project.py`
9. The web application will launch on `localhost:8050`
