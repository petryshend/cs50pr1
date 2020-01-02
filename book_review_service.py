from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from book_review import BookReview
from params import DATABASE_URL


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
            'book_id': review.book.book_id,
            'user_id': review.user.id,
            'review_text': review.review_text,
            'rate': review.rate
        })
        self.db.commit()

        return review