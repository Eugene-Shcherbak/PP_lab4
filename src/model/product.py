from src.main import app,db
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import reqparse
from flask_sqlalchemy import SQLAlchemy


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    text = db.Column(db.String(50), unique=True, nullable=False)
    state = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def save(self):
        return{
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'state': self.state,
            'category': self.category,
        }

    def save_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, myid):
        return Product.query.filter_by(id=myid).first()

    @classmethod
    def get_by_title(cls, mytitle):
        return Product.query.filter_by(title=mytitle).first()

    #дороби ерори
    @classmethod
    def delete(cls, myid):
        product = Product.get_by_id(myid)
        product_json = product.save(product)
        product.query.filter_by(id=myid).delete()
        db.session.commit()
        return product_json

    @app.route("/product", methods=['POST', 'PUT'])
    def product():
        if request.method == 'POST':
            pars = reqparse.RequestParser()
            pars.add_argument('id', help='name cannot be blank', required=True)
            pars.add_argument('title', help='name cannot be blank', required=True)
            pars.add_argument('text', help='name cannot be blank', required=True)
            pars.add_argument('state', help='status cannot be blank', required=True)
            pars.add_argument('category', help='status cannot be blank', required=True)

            data = pars.parse_args()
            try:
                id = int(data['id'])
            except Exception:
                return {"message": "error"}, 500

            title = data['title']
            text = data['text']
            state = data['state']
            category = data['category']

            product_1 = Product(
                title=title,
                text=text,
                state=state,
                category=category
            )
            try:
                product_1.add_to()
                return {"message": "new product added"}, 200
            except Exception:
                return {"message": "error"}, 405

        elif request.method == 'PUT':
            pars = reqparse.RequestParser()
            pars.add_argument('id', help='name cannot be blank', required=True)
            pars.add_argument('title', help='name cannot be blank', required=True)
            pars.add_argument('text', help='name cannot be blank', required=True)
            pars.add_argument('state', help='status cannot be blank', required=True)
            pars.add_argument('category', help='status cannot be blank', required=True)

            data = pars.parse_args()
            id = int(data['id'])

            try:
                product_1 = Product.query.filter_by(id=id).update(data)
                db.session.commit()
                return {"message": "product is updated"}, 200
            except Exception:
                return {"message": "error"}, 500
