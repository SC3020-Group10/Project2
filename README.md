# Project2: Query Analyzer

# Installation
1. Install `PostgreSQL` [here](https://www.postgresql.org/download/)
2. Download the TPC-H csv files [here](https://drive.google.com/drive/folders/1sAwyOoHuS35j6GTRL8-COcknz6Lo1S9k?usp=sharing)
3. Import the TPC-H dataset into your PostgreSQL database
4. Navigate to the root of the project
5. Create a new python environment and install the dependencies using `pip install -r requirements.txt`
6. Create a `.env` file in the root of the project if it is not present
7. Add or update these environment variables in the `.env` file
```
DATABASE: The name of your database.
USER: Your database username.
PASSWORD: Your database password.
HOST: The hostname or IP address of your database server.
PORT: The port number your database server is listening on.
```
8. Start the web application using `python project.py` or `python3 project.py`
