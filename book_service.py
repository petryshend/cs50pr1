from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from book import Book
from params import DATABASE_URL


class BookService:

    def __init__(self):
        engine = create_engine(DATABASE_URL)
        self.db = scoped_session(sessionmaker(bind=engine))

    def search(self, query: str):
        q = """
        SELECT * 
        FROM books
        WHERE title ILIKE :query
            OR author ILIKE :query
            OR isbn ILIKE :query
        """
        res = self.db.execute(q, {'query': "%" + query + "%"})
        books = []
        for id, isbn, title, author, year in res.fetchall():
            books.append(Book(id, isbn, title, author, year))

        return books
