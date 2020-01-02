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
        SELECT book_id, isbn, title, author, year 
        FROM books
        WHERE title ILIKE :query
            OR author ILIKE :query
            OR isbn ILIKE :query
        """
        res = self.db.execute(q, {'query': "%" + query + "%"})
        books = []
        for book_id, isbn, title, author, year in res.fetchall():
            books.append(Book(book_id, isbn, title, author, year))

        return books

    def get_by_id(self, book_id):
        q = """
        SELECT book_id, isbn, title, author, year
        FROM books
        WHERE book_id = :book_id
        """
        res = self.db.execute(q, {'book_id': book_id})
        row = res.fetchone()

        return Book(*row)
