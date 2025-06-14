from app import app, db
from app.models import Category, Keyword, Transaction
import os

def init_db():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Import existing categories from categorias.json if it exists
        if os.path.exists('categorias.json'):
            import json
            with open('categorias.json', 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
                
            # Create categories and keywords
            for keyword, category_name in categories_data.items():
                # Check if category exists
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.flush()  # Get the category ID
                
                # Add keyword if it doesn't exist
                if not Keyword.query.filter_by(word=keyword).first():
                    keyword_obj = Keyword(word=keyword, category_id=category.id)
                    db.session.add(keyword_obj)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 