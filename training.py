from sqlalchemy import create_engine
import pandas as pd

from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise import dump

from db_util import get_db_conn_url

def train(path):
    db_uri = f'postgres+psycopg2://{get_db_conn_url()}'
    engine = create_engine(db_uri, echo=True)

    ratings_df = pd.read_sql(
        "SELECT r.user_id, r.movie_id, r.rating, r.timestamp FROM ratings r INNER JOIN (SELECT user_id FROM ratings GROUP BY user_id HAVING COUNT(*) >= 5) o ON r.user_id = o.user_id",
        con = engine
    )

    reader = Reader(rating_scale=(0.5,5))
    data = Dataset.load_from_df(ratings_df[['user_id', 'movie_id', 'rating']], reader)
    trainset = data.build_full_trainset()

    algo = SVD()
    algo.fit(trainset)

    dump.dump(path, algo=algo, verbose=1)
    return algo