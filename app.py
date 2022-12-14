from crypt import methods
from re import S
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

@app.cli.command('db_create')
def db_create(): 
    db.create_all()
    print("DB created")

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('DB dropped')

@app.cli.command('db_seed')
def db_seed():
    earth = Planet(planet_name='earth', planet_type='class M', home_star='sol', mass=1.258e23, radius=6816, distance=9.98e6)
    venus = Planet(planet_name='venus', planet_type='class k', home_star='sol', mass=4.258e23, radius=2416, distance=95.98e6)
    mercury = Planet(planet_name='mercury', planet_type='class D', home_star='sol', mass=3.258e23, radius=1516, distance=35.98e6)

    db.session.add(earth)
    db.session.add(venus)
    db.session.add(mercury)

    test_user = User(first_name='daskikey', last_name='ayy', email='asdf', password='password')
    db.session.commit()
    print('DB seeded')

@app.route('/')
def ello_world():
    return jsonify(message='Ello Chap')


@app.route('/super_simple')
def super_simple():
    return jsonify(message='ell chap fromsd api'), 200


@app.route('/not_found')
def note_found():
    return jsonify(message='That resource was not found'), 404


@app.route('/params')
def params():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message='Sorry ' + name + ', to young'), 401
    else: 
        return jsonify(message='Welcome ' + name + ' you are old enough'), 200


@app.route('/url_vars/<string:name>/<int:age>')
def url_vars(name: str, age: int):
    if age < 18:
        return jsonify(message='Sorry ' + name + ', to young'), 401
    else: 
        return jsonify(message='Welcome ' + name + ' you are old enough'), 200


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    print(result)
    return jsonify(result)

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Email already exists'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name = first_name, last_name=last_name, email= email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Succeeded', access_token=access_token)
    else:
        return jsonify(message='Bad email or password'), 401


#database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta: 
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

class PlanetSchema(ma.Schema):
    class Meta: 
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_start', 'mass', 'radius', 'distance')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__name__':
    app.run()