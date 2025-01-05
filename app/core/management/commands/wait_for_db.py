from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2OpError

import time

#from pyscopg2 import OperationError as Psycopg2OpError

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("waiting for database")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, Psycopg2OpError):
                self.stdout.write("Databse unavailable! waiting for 1 second")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))

        