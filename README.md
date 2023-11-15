# Project2: Query Analyzer

# Installation

1. Install `PostgreSQL` [here](https://www.postgresql.org/download/)
2. Clone this repository using `git clone https://github.com/SC3020-Group10/Project2.git`
3. Navigate to the root folder of this project
4. Download and unzip the TPC-H csv files and sql setup files [here](https://drive.google.com/drive/folders/1sAwyOoHuS35j6GTRL8-COcknz6Lo1S9k?usp=sharing) and place it into the root folder.
5. Create a new python environment using a package manager such as `venv` or `conda` (Note: This project was tested on python 3.11)

**venv**

```bash
python -m venv myenv
myenv\Scripts\activate
```

**conda**

```bash
conda create -n ENV_NAME python=3.11
conda activate ENV_NAME
conda install pip
```

6. Install python dependencies and import the TPC-H dataset into your PostgreSQL database by running `./setup.sh [Your PostgreSQL username] [Your PostgreSQL password]` if you are using bash or `setup.bat [Your PostgreSQL username] [Your PostgreSQL password]` if you are using command prompt

Note: If TPC-H database is already installed locally, you can instead run `python -m pip install -r requirements.txt` to install the dependencies and create a `.env` file in the root folder. The .env file should be in this format

```env
username=[Your PostgreSQL username]
password=[Your PostgreSQL password]
database=[Your PostgreSQL database]
host=[IP address of your PostgreSQL server]
port=[The port number your PostgreSQL server is listening on]
```

7. Start the web application using `python project.py` or `setup.bat` or `./setup.sh`
8. The web application will launch on `localhost:8050`
