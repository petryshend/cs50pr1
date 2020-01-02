from book import Book
from user import User


class BookReview:
    def __init__(self, book: Book, user: User, review_text: str, rate: int):
        self.book = book
        self.user = user
        self.review_text = review_text
        self.rate = rate
