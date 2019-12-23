import os
import csv
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

if __name__ == '__main__':
    file = open('books.csv')
    reader = csv.reader(file)
    next(reader) # skip header
    start_time = int(time.time())
    for isbn, title, author, year in reader:
        query = """
        INSERT INTO books (isbn, title, author, year)
        VALUES (:isbn, :title, :author, :year)
        """
        db.execute(query, {'isbn': isbn, 'title': title, 'author': author, 'year': year})
        print('Book "' + title + '" added')
    db.commit()
    execution_time = int(time.time()) - start_time
    print(str(execution_time) + ' seconds passed')
