# Lego Stocktaking Database
>A python web-based server application for documenting Lego inventories for collectors and resellers.

## Features
Python based server application that uses flask and bootstrap to render web pages, allowing a user to access the database from any device on the network.

## Requirements
* Python 3.7
* Pip
* virtualenv
* Bricklink registered seller credentials.

## Installation & Running
### Manual:
Change json file with bricklink credendtials in app/data/auth.json to access bricklink API. 
For more information on obtaining API credentials, see: https://www.bricklink.com/v2/api/register_consumer.page 

Setup virtualenv:
```{bash}
$ virtualenv venv
$ source venv/bin/activate
```
If virtualenv is active:
```{bash}
$ pip install -r requirements.txt
$ python run.py
```
### Docker:
To be supported...
## Technologies
* Python 3.7
* Flask
* Bootstrap 4.5
* SQL-Alchemy
* Bricklink python API
