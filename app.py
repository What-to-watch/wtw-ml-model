import os
from surprise import dump
from training import train
from db_util import get_db_conn_url

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{get_db_conn_url()}"
db = SQLAlchemy(app)

from sqlalchemy import text

model_dump_path = "model_dump"

@app.route('/topN/<user_id>')
def getTopN(user_id):
    n = request.args.get('n')
    if n is None:
        n = 5
    else:
        n = int(n)
    
    model = get_model()

    query = text("SELECT id FROM movies WHERE id NOT IN (SELECT movie_id FROM ratings WHERE user_id = :user_id)")
    result = db.engine.execute(query, user_id=user_id).fetchall()

    movies = map(lambda row: { "movie_id": row[0], "prediction":model.predict(user_id, row[0]).est}, result)
    movies = sorted(movies, key=lambda m: m["prediction"], reverse=True)

    return {
        "movies":movies[:n]
    }
    


@app.route('/predict')
def predict():
    model = get_model()
    req = request.get_json()
    return {
        "prediction": model.predict(req['user'], req['movie']).est
    }

def get_model():
    path = os.path.normpath(model_dump_path)
    if os.path.isfile(path):
        _, loaded_algo = dump.load(path)
        return loaded_algo
    else:
        algo = train(path)
        return algo