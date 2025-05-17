

---

# Python Generators & MySQL Seeding

## Project Overview

This project demonstrates the use of Python generators and MySQL database integration to efficiently handle large datasets. It focuses on creating a generator that streams rows from a database one by one—ideal for memory-efficient data processing.

## Features

* Set up and seed a MySQL database (`ALX_prodev`) with a `user_data` table.
* Populate the table using data from a `user_data.csv` file.
* Ensure table creation and avoid duplicate entries.
* Lay the foundation for using Python generators to stream data row-by-row.

## Table Schema

| Column   | Type    | Attributes           |
| -------- | ------- | -------------------- |
| user\_id | UUID    | PRIMARY KEY, INDEXED |
| name     | VARCHAR | NOT NULL             |
| email    | VARCHAR | NOT NULL             |
| age      | DECIMAL | NOT NULL             |

## How It Works

1. `connect_db()` – Connects to the MySQL server.
2. `create_database(connection)` – Creates `ALX_prodev` database if it doesn’t exist.
3. `connect_to_prodev()` – Connects to the `ALX_prodev` database.
4. `create_table(connection)` – Creates the `user_data` table.
5. `insert_data(connection, 'user_data.csv')` – Populates the table using the CSV file.

## Sample Output

```
connection successful  
Table user_data created successfully  
Database ALX_prodev is present  
[('00234e50-...', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), ...]
```

## Getting Started

### Prerequisites

* Python 3.x
* MySQL Server
* `mysql-connector-python` (install via `pip install mysql-connector-python`)

### Usage

Run the main script to set up and populate the database:

```bash
./0-main.py
```

Ensure `user_data.csv` is in the same directory.

## Next Steps

Implement a Python generator to stream rows from the `user_data` table one-by-one, enabling scalable data processing.

---

