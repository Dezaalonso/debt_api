from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, inspect

app = Flask(__name__)

# Configuration for multiple databases
app.config['SQLALCHEMY_BINDS'] = {
    'db_user': 'mysql://admin:Cloud998134@cloudpp1.cv478kobasse.us-east-1.rds.amazonaws.com/user_db',
    'db_debt': 'mysql://admin:Cloud998134@cloudpp1.cv478kobasse.us-east-1.rds.amazonaws.com/debt_db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "somethingunique"

db = SQLAlchemy(app)

# Define models, binding each to its respective database
class User(db.Model):
    __bind_key__ = 'db_user'
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)


class Debt(db.Model):
    __bind_key__ = 'db_debt'
    __tablename__ = 'debt'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    debt = db.Column(db.Integer)

def table_exists(engine, table_name):
    inspector = inspect(engine)
    return inspector.has_table(table_name)

with app.app_context():
    engines = {
        'db_user': db.get_engine(bind='db_user'),
        'db_debt': db.get_engine(bind='db_debt')
    }
    
    # Check and create tables for each bind
    for bind_key, engine in engines.items():
        metadata = MetaData()
        metadata.reflect(bind=engine)
        if not table_exists(engine, 'user') and bind_key == 'db_user':
            User.__table__.create(bind=engine)

        if not table_exists(engine, 'debt') and bind_key == 'db_debt':
            Debt.__table__.create(bind=engine)

@app.route('/debts', methods=['GET'])
def get_all_debts():
    # Retrieve all debts
    all_debts = Debt.query.all()
    
    # Prepare the response with debt information
    if all_debts:
        debt_info = [{'debt_id': debt.id, 'user_id': debt.user_id, 'debt': int(debt.debt)} for debt in all_debts]
        return jsonify(debt_info), 200
    else:
        return jsonify({'message': 'No debts found'}), 404

@app.route('/debts/<int:user_id>', methods=['POST'])
def create_debt(user_id):
    debt_value = request.json.get('debt')
    
    # Check if the user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create a new debt entry for the user
    new_debt = Debt(user_id=user.id, debt=debt_value)
    db.session.add(new_debt)
    db.session.commit()

    return jsonify({'message': 'Debt created successfully', 'debt_id': new_debt.id}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

