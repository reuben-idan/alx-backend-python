import time
import os
import mysql.connector
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                # Try to connect to MySQL database
                db_conn = mysql.connector.connect(
                    host=os.environ.get('MYSQL_HOST', 'db'),
                    port=int(os.environ.get('MYSQL_PORT', 3306)),
                    user=os.environ.get('MYSQL_USER', 'messaging_user'),
                    password=os.environ.get('MYSQL_PASSWORD', 'messaging_password123'),
                    database=os.environ.get('MYSQL_DATABASE', 'messaging_db')
                )
            except mysql.connector.Error:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!')) 