from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from book import Book
from book_review import BookReview
from params import DATABASE_URL
from user import User


class BookReviewService:

    def __init__(self):
        engine = create_engine(DATABASE_URL)
        self.db = scoped_session(sessionmaker(bind=engine))

    def insert(self, review: BookReview) -> BookReview:
        q = """
        INSERT INTO book_review (book_id, user_id, review_text, rate) 
        VALUES (:book_id, :user_id, :review_text, :rate)
        """
        self.db.execute(q, {
            'book_id': review.book.id,
            'user_id': review.user.id,
            'review_text': review.review_text,
            'rate': review.rate
        })
        self.db.commit()

        return review

    def get_by_book_and_user(self, book: Book, user: User):
        q = """
        SELECT review_text, rate
        FROM book_review
        WHERE book_id = :book_id
            AND user_id = :user_id
        """
        res = self.db.execute(q, {
            'book_id': book.id,
            'user_id': user.id
        })
        row = res.fetchone()
        if row:
            return BookReview(book=book, user=user, review_text=row['review_text'], rate=row['rate'])
        return None
