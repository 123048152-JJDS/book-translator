from app import db
from datetime import datetime, timezone
import re


def slugify(text):
    """Convert book title to a safe filename prefix."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    return text[:40]


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200))
    slug = db.Column(db.String(60), nullable=False)
    description = db.Column(db.Text)
    source_language = db.Column(db.String(50), default='English')
    target_language = db.Column(db.String(50), default='Spanish')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    pages = db.relationship('Page', backref='book', lazy=True, cascade='all, delete-orphan',
                            order_by='Page.page_number')

    def __repr__(self):
        return f'<Book {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'slug': self.slug,
            'description': self.description,
            'source_language': self.source_language,
            'target_language': self.target_language,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'total_pages': len(self.pages),
            'translated_pages': sum(1 for p in self.pages if p.translation and p.translation.strip()),
        }


class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(300), nullable=False)
    original_text = db.Column(db.Text)       # extracted or typed original text
    translation = db.Column(db.Text)          # manual translation
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending | in_progress | done
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    __table_args__ = (
        db.UniqueConstraint('book_id', 'page_number', name='uq_book_page'),
    )

    def __repr__(self):
        return f'<Page {self.book_id}-{self.page_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'page_number': self.page_number,
            'image_filename': self.image_filename,
            'image_url': f'/static/uploads/{self.image_filename}',
            'original_text': self.original_text or '',
            'translation': self.translation or '',
            'notes': self.notes or '',
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
