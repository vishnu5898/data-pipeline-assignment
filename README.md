# DATA PIPELINE ASSIGNMENT

## Scope
### Pipeline Implementation
##### `Architecture Diagram`
![alt text](architecture_diagram.png)
To be filled

##### `Key points`

1. A mock API to simulate real-time market data is set. The api demonstrates real-time-data api from stock market.
2. A basic and simple pipeline that ingests, processes and stores this data is designed and implemented.
3. The pipeline only works in a real-time manner till the data ingestion and storage to Postgresql table.
4. Tableau cannot be incorporated with this pipeline as it is not a paid version, but images of dashboard are attached.


### Data Governance and Data Structures
##### `Key points`
1. A basic data governance framework suitable for market data is outlined.
2. A dabase schema is devloped and implemented it using a `Postgresql` database.


### Python Scripting
1. A python script is written to simulate data scraping (ingestion), to perform necessary transformation required to store the data in the postgresql table.

### Tableau Visualization
1. A Tableau dashboard was developed that includes 3 different types of visualizations: time-series chart, bar chart, heatmap.
2. The dashboard created is interactive and user-friendly.

## Out of scope
### Pipeline Implementation
##### `Architecture Diagram`
To be filled
##### `Key points`
1. The above architecture diagram is more efficient in cost and performance, loosely coupled and easy to manage.
2. The architecture diagram given above is not implemented due to
- lack of infrastructure available to test locally
- lack of time to set up and implement a large solution

### Tableau Visualization
1. A real-time dashboard cannot be made as the Tableau public available for free does not have the features to connect to postgresql database.


## How to setup
#### Install dependencies
1. Clone this repository
```
git clone git@github.com:vishnu5898/data-pipeline-assignment.git
```
If did not work, download the zip file and unzip the file.

2. Change the directory
```
cd data-pipeline-assignment
```
3. Install dependencies
```
sudo apt update
sudo apt install virtualenv
```
4. Create virtual environment and activate it
```
virtualenv -p python3.10 .venv
source .venv/bin/activate
```
5. Install the python dependencies
```
pip install -r requirements.txt
```

#### Setup Postgresql database
1. Install postgres locally
```
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

sudo apt-get update
sudo apt-get -y install postgresql
```
2. Create database, username and password. Run this command in terminal `sudo su postgres`. Now you will be logged in as postgres user. Enter `psql` in command line. Now you will be logged in to psql client. After that run these commands to create database and username. Instead of `test_user` and `test_password` use your username and password.
```
CREATE DATABASE market_data;
CREATE USER test_user USING PASSWORD 'test_password';
ALTER DATABASE market_data OWNER TO test_user;
```
3. Now you quit the psql client by running `\q` in interactive session.
4. Once you are out of the psql client session. Enter `exit` to come back to the default user session in terminal window.

#### Run pipeline
1. We have to provide credentials of the database to which the igested data can be stored
2. Run the commands to start the server for stock data mock api
```
source env.sh
python -m server
```
3. Open another terminal session and change directory to this repository
```
cd data-pipeline-assignment
```
Create a new file `env.sh`. Run this command to create the file `touch env.sh`. Paste the below variables and values to this file and then save the file. Please make sure to give the correct value to the variable.
```
PG_USERNAME=test_user
PG_PASSWORD=test_password
PG_DATABASE=market_data
```
Run these commands in the terminal to start the pipeline
```
source .venv/bin/activate
source env.sh
python -m main
```