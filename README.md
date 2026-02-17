💳 ATM Management System (Database Version)
🚀 Project Overview

This is a fully functional ATM Management System built using Python and MySQL.

Initially, this project was developed using file handling.
It has now been upgraded to a database-driven system, making it more secure, scalable, and structured — just like real banking systems.

This upgrade reflects my growth from basic Python scripting to backend system design.

🛠 Technologies Used

Python 3

MySQL

mysql-connector-python

SHA-256 Hashing (for PIN security)

🔐 Key Features
👤 User Panel

Secure Login (Hashed PIN)

Check Balance

Withdraw Money

Deposit Money

Transfer Money

Change PIN

View Transaction History

🛠 Admin Panel

View All Accounts

Create New Account

Delete Account

View Account Transaction History

Change Admin Password

🔒 Security Features

PINs stored using SHA-256 hashing

Transaction rollback for safe money transfers

Attempt limit on login

Separate Admin & User roles

📊 Database Structure
accounts Table

acc_no

acc_holder_name

pin (hashed)

balance

acc_type

transactions Table

id

acc_no

transaction_type

amount

detail

transaction_date
