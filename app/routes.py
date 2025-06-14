from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from app.models import Category, Keyword, Transaction
from datetime import datetime
from thefuzz import process
import json
import os
import re
import pdfplumber
from dateutil import parser
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_transactions_from_pdf(pdf_path):
    transactions = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # This pattern needs to be adjusted based on your bank's PDF format
                patterns = [
                    # Pattern 1: DD/MM/YYYY Description Amount
                    r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?\d+[.,]\d{2})',
                    # Pattern 2: DD/MM Description Amount
                    r'(\d{2}/\d{2})\s+(.*?)\s+(-?\d+[.,]\d{2})',
                    # Add more patterns as needed
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        date_str, description, amount_str = match.groups()
                        try:
                            # Try to parse the date
                            if len(date_str.split('/')) == 2:
                                date = parser.parse(date_str).replace(year=datetime.now().year)
                            else:
                                date = parser.parse(date_str)
                            
                            # Parse amount
                            amount = float(amount_str.replace('.', '').replace(',', '.'))
                            
                            transactions.append({
                                'date': date,
                                'description': description.strip(),
                                'amount': amount
                            })
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing transaction: {e}")
                            continue
    except Exception as e:
        print(f"Error processing PDF: {e}")
        flash(f'Erro ao processar o PDF: {str(e)}', 'error')
    
    return transactions

@app.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    categories = Category.query.all()
    
    # Calculate totals
    debit_total = sum(t.amount for t in transactions if not t.is_credit)
    credit_total = sum(abs(t.amount) for t in transactions if t.is_credit)
    
    return render_template('index.html', 
                         transactions=transactions, 
                         categories=categories,
                         debit_total=debit_total,
                         credit_total=credit_total)

@app.route('/upload', methods=['POST'])
def upload_transactions():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        if filename.endswith('.pdf'):
            transactions = extract_transactions_from_pdf(filepath)
        else:
            content = file.read().decode('utf-8')
            transactions = process_transactions(content)
        
        # Process each transaction
        for trans in transactions:
            if isinstance(trans, dict):  # PDF transaction
                transaction = Transaction(
                    date=trans['date'],
                    description=trans['description'],
                    amount=trans['amount'],
                    is_credit=trans['amount'] < 0
                )
            else:  # Text file transaction
                date_str, description, amount = parse_transaction(trans)
                if date_str and amount:
                    date = datetime.strptime(date_str, '%m/%d').replace(year=datetime.now().year)
                    transaction = Transaction(
                        date=date,
                        description=description,
                        amount=amount,
                        is_credit=amount < 0
                    )
                else:
                    continue
            
            # Try to categorize automatically
            category = auto_categorize(transaction.description)
            if category:
                transaction.category = category
            
            db.session.add(transaction)
        
        db.session.commit()
        flash('Transações importadas com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao processar arquivo: {str(e)}', 'error')
    finally:
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
    
    return redirect(url_for('index'))

@app.route('/categorize/<int:transaction_id>', methods=['POST'])
def categorize_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    category_id = request.form.get('category_id')
    
    if category_id:
        category = Category.query.get(category_id)
        transaction.category = category
        db.session.commit()
        
        # Add keyword if provided
        keyword = request.form.get('keyword')
        if keyword and not Keyword.query.filter_by(word=keyword).first():
            new_keyword = Keyword(word=keyword, category_id=category_id)
            db.session.add(new_keyword)
            db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name and not Category.query.filter_by(name=name).first():
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
        return redirect(url_for('manage_categories'))
    
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/keyword/<int:keyword_id>', methods=['DELETE'])
def delete_keyword(keyword_id):
    keyword = Keyword.query.get_or_404(keyword_id)
    db.session.delete(keyword)
    db.session.commit()
    return '', 204

@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    category_id = request.form.get('category_id')
    keyword = request.form.get('keyword')
    
    if category_id and keyword:
        if not Keyword.query.filter_by(word=keyword).first():
            new_keyword = Keyword(word=keyword, category_id=category_id)
            db.session.add(new_keyword)
            db.session.commit()
            flash('Palavra-chave adicionada com sucesso!', 'success')
        else:
            flash('Esta palavra-chave já existe!', 'warning')
    
    return redirect(url_for('manage_categories'))

def process_transactions(input_text):
    lines = input_text.strip().split("\n")
    transactions = []
    current_transaction = []
    date_pattern = re.compile(r'^\d{1,2}/\d{1,2}')

    for line in lines:
        if date_pattern.match(line.strip()):
            if current_transaction:
                transactions.append(" ".join(current_transaction).strip())
                current_transaction = []
            current_transaction.append(line.strip())
        else:
            current_transaction.append(line.strip())

    if current_transaction:
        transactions.append(" ".join(current_transaction).strip())

    return transactions

def parse_transaction(transaction_text):
    # Extract date (MM/DD format)
    date_match = re.search(r'^(\d{1,2}/\d{1,2})', transaction_text)
    if not date_match:
        return None, None, None
    
    date_str = date_match.group(1)
    
    # Extract amount (last number in the string)
    amount_match = re.search(r'-?\d+(?:[\.,]\d{1,2})?$', transaction_text)
    if not amount_match:
        return date_str, transaction_text, None
    
    amount_str = amount_match.group(0)
    amount = parse_monetary_value(amount_str)
    
    # Description is everything between date and amount
    description = transaction_text[len(date_str):amount_match.start()].strip()
    
    return date_str, description, amount

def parse_monetary_value(value_str):
    value_str = value_str.strip()
    value_str = value_str.replace('.', '')
    value_str = value_str.replace(',', '.')
    try:
        return float(value_str)
    except ValueError:
        return None

def auto_categorize(description):
    # Get all keywords with their categories
    keywords = Keyword.query.all()
    if not keywords:
        return None
    
    # Create a list of (keyword, category) tuples
    keyword_categories = [(k.word, k.category) for k in keywords]
    
    # Use fuzzy matching to find the best match
    best_match = process.extractOne(
        description.lower(),
        [k[0].lower() for k in keyword_categories],
        score_cutoff=80  # Minimum similarity score (0-100)
    )
    
    if best_match:
        # Find the category for the matched keyword
        matched_keyword = best_match[0]
        for keyword, category in keyword_categories:
            if keyword.lower() == matched_keyword:
                return category
    
    return None 