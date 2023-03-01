# Budgeter
#### Video Demo: 

## Overview
Budgeter is a simple and user-friendly budgeting tool that helps users to keep track of their financial habits, whether it is about spending or earning money.
Budgeter is divided into three separate applications, the authenticator, the budgeter and the wallet. Its modularity allows for re-usability and ease of maintenance.


## Contents
- The **user documentation** presents the main functionalities of Budgeter, provides thorough installation instructions and gives tips on how to use the application’s main dashboard.
- The **system documentation** includes details on the application backlog, information architecture, user-flow scheme and models included in the project.


## Objectives
Budgeter aims to provide an intuitive application that enables users to record and manage their day-to-day financial transactions, including expenditures and earnings.

- ```Keep track of your financial habits```: Create, read, update and delete budget entries, or simply navigate through past transactions and learn where all you money goes and comes from.
- ```Filter & search with ease```: Filter entries based on categories and transaction types.
- ```Find everything you need```: Look up entries using key words, such as names, types, categories and notes.
- ```See what’s going on```: See statistics at a glance and rewind the previous six months by looking at cash-flow trends.
- ```Manage account & settings```: Make your account your very own and change regional settings.


## Installation guide
    ```
    # Clone the repository and open the project’s folder
    $ git clone https://github.com/andreicsandor/project-rainier.git
    
    # Set up the virtual environment and install the requirements
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    
    # Make the initial migrations
    $ cd rainier
    $ python manage.py makemigrations
    $ python manage.py makemigrations
    $ python manage.py makemigrations
    $ python manage.py makemigrations
    $ python manage.py migrate authenticator $ python manage.py migrate budgeter
    $ python manage.py migrate wallet
    $ python manage.py migrate
    
    # Create the superuser
    $ python manage.py createsuperuser
    # Load the initial fixtures into the database
    $ python manage.py loaddata type
    $ python manage.py loaddata category
    $ python manage.py loaddata currency
    $ python manage.py loaddata profile
    $ python manage.py loaddata transaction
    
    # Run the server
    $ python manage.py runserver
    ```
