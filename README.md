# CLI-Twitter-Mockup

This Python project allows a user to query and interface with a SQL database using a Python Command Line Interface. This project contains a SQL script which generates a SQL database constructed using real Twitter data including several thousand tweets and user profiles which can be interacted with using this project.

## Installation

Start a MySQL instance and edit TwitterInterface.py by inputting your credentials on lines 100-101  

In order to run the code one needs to import sqlalchemy, pymysql and cryptography installing any modules that the interpreter does not recognize. They also need a MYSQL instance with a username and password to use to connect to the database with all necessary permissions enabled. The database itself has to be ready for use by running the SQL script that instantiates a database named twitterDB. The hostname also needs to be known for the connection to work. The program will request a username to represent who is signing onto the social media platform. Any username from within the users database is valid (e.g. 2v (this also happens to be one of the shortest and easier to type names)). For more detailed explanation of the code please consult the code and the comments in the code.  

## How to use

[![IMAGE ALT TEXT](http://img.youtube.com/vi/TKPDEqXJdto/0.jpg)](http://www.youtube.com/watch?v=TKPDEqXJdto "Video Title")
