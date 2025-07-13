# 0x02-redis_basic

This project demonstrates basic usage of Redis in Python, including storing and retrieving data using a custom Cache class. The `exercise.py` module provides a simple interface for writing strings and other data types to a Redis database, with automatic key generation and type annotations.

## Features

- Store data of type `str`, `bytes`, `int`, or `float` in Redis
- Automatically generates unique keys for each entry
- Uses Redis as a backend for fast, in-memory storage
- Includes full documentation and type annotations

## Requirements

- Python 3.7+
- `redis` Python package
- Redis server (local or containerized)

## Usage

See the example in the project description or use the `Cache` class directly in your own scripts.
