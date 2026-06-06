import os
# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify, render_template, current_app
from app import db
from app.models import Book, slugify

books_bp = Blueprint('books', __name__)


@books_bp.route('/')
def index():
    return render_template('index.html')


@books_bp.route('/books/<int:book_id>/translate')
def translate_view(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('translate.html', book=book)


# ── API ──────────────────────────────────────────────────────────────────────

@books_bp.route('/api/books', methods=['GET'])
def list_books():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return jsonify([b.to_dict() for b in books])


@books_bp.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    book = Book(
        title=data['title'].strip(),
        author=data.get('author', '').strip(),
        slug=slugify(data['title']),
        description=data.get('description', '').strip(),
        source_language=data.get('source_language', 'English'),
        target_language=data.get('target_language', 'Spanish'),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@books_bp.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    for field in ('title', 'author', 'description', 'source_language', 'target_language'):
        if field in data:
            setattr(book, field, data[field].strip())
    if 'title' in data:
        book.slug = slugify(data['title'])
    db.session.commit()
    return jsonify(book.to_dict())


@books_bp.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Delete all physical images associated with this book's pages
    upload_folder = current_app.config['UPLOAD_FOLDER']
    for page in book.pages:
        img_path = os.path.join(upload_folder, page.image_filename)
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting page image {img_path}: {e}")
                
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})
