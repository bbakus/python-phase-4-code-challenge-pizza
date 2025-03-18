#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurant_dict = [rest.to_dict(only=('address', 'id', 'name')) for rest in restaurants]
        return make_response(jsonify(restaurant_dict), 200)
    
api.add_resource(Restaurants, '/restaurants')

class RestaurantsID(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return make_response(jsonify(restaurant.to_dict()), 200)
        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return make_response(jsonify(response_body), 404)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response(jsonify({}), 204)
        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return make_response(jsonify(response_body), 404)


api.add_resource(RestaurantsID, '/restaurants/<int:id>')


class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizza_dict = [p.to_dict(only=('id', 'ingredients', 'name')) for p in pizzas]
        return make_response(jsonify(pizza_dict), 200)
    
api.add_resource(Pizzas, '/pizzas')


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        
        except ValueError:
            return make_response(
                jsonify({"errors": ["validation errors"]}),
                400
            )

api.add_resource(RestaurantPizzas, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
