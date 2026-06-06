import os
# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify, current_app
# pyrefly: ignore [missing-import]
from werkzeug.utils import secure_filename
from app import db
from app.models import Book, Page

pages_bp = Blueprint('pages', __name__)


def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower()
        in current_app.config['ALLOWED_EXTENSIONS']
    )


def build_image_filename(book: Book, page_number: int, original_filename: str) -> str:
    """
    Return a descriptive filename:
        <book_slug>_p<page_number_padded>.<ext>
    Example: learning_english_p007.jpg
    """
    ext = original_filename.rsplit('.', 1)[1].lower()
    return f"{book.slug}_p{page_number:04d}.{ext}"


@pages_bp.route('/api/books/<int:book_id>/pages', methods=['GET'])
def list_pages(book_id):
    Book.query.get_or_404(book_id)
    pages = Page.query.filter_by(book_id=book_id).order_by(Page.page_number).all()
    return jsonify([p.to_dict() for p in pages])


@pages_bp.route('/api/books/<int:book_id>/pages', methods=['POST'])
def upload_page(book_id):
    book = Book.query.get_or_404(book_id)

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Determine next page number (or use provided)
    page_number = request.form.get('page_number')
    if page_number:
        page_number = int(page_number)
        existing = Page.query.filter_by(book_id=book_id, page_number=page_number).first()
        if existing:
            return jsonify({'error': f'Page {page_number} already exists'}), 409
    else:
        last = (
            Page.query.filter_by(book_id=book_id)
            .order_by(Page.page_number.desc())
            .first()
        )
        page_number = (last.page_number + 1) if last else 1

    filename = build_image_filename(book, page_number, file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    page = Page(
        book_id=book_id,
        page_number=page_number,
        image_filename=filename,
        original_text=request.form.get('original_text', ''),
        status='pending',
    )
    db.session.add(page)
    db.session.commit()
    return jsonify(page.to_dict()), 201


@pages_bp.route('/api/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    page = Page.query.get_or_404(page_id)
    return jsonify(page.to_dict())


@pages_bp.route('/api/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    page = Page.query.get_or_404(page_id)
    data = request.get_json()

    for field in ('original_text', 'translation', 'notes'):
        if field in data:
            setattr(page, field, data[field])

    if 'status' in data:
        page.status = data['status']
    elif 'translation' in data:
        # Auto-update status based on translation content only if status is not explicitly passed
        if data['translation'] and data['translation'].strip():
            page.status = 'done'
        else:
            page.status = 'pending'

    db.session.commit()
    return jsonify(page.to_dict())


@pages_bp.route('/api/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    filename = page.image_filename
    db.session.delete(page)
    db.session.commit()
    
    # Remove physical image file post-commit
    upload_folder = current_app.config['UPLOAD_FOLDER']
    img_path = os.path.join(upload_folder, filename)
    if os.path.exists(img_path):
        try:
            os.remove(img_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting page image file {img_path}: {e}")
            
    return jsonify({'message': 'Page deleted'})


@pages_bp.route('/api/books/<int:book_id>/pages/reorder', methods=['POST'])
def reorder_pages(book_id):
    """Accept [{id, page_number}, ...] and update order."""
    Book.query.get_or_404(book_id)
    data = request.get_json()
    
    # Pass 1: Set temporary negative page numbers to avoid UniqueConstraint conflicts
    for item in data:
        page = Page.query.get(item['id'])
        if page and page.book_id == book_id:
            page.page_number = -int(item['page_number'])
    db.session.flush()
    
    # Pass 2: Set final positive page numbers
    for item in data:
        page = Page.query.get(item['id'])
        if page and page.book_id == book_id:
            page.page_number = int(item['page_number'])
            
    db.session.commit()
    return jsonify({'message': 'Reordered'})
