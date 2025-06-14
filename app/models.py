from datetime import datetime
from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    keywords = db.relationship('Keyword', backref='category', lazy=True)
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Keyword {self.word}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_credit = db.Column(db.Boolean, default=False)  # True for credits (negative amounts), False for debits

    def __repr__(self):
        return f'<Transaction {self.description} {self.amount}>'

    @property
    def formatted_amount(self):
        return f"R$ {abs(self.amount):,.2f}"

    @property
    def formatted_date(self):
        return self.date.strftime("%d/%m/%Y") 