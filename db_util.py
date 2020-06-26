import os

def get_db_conn_url():
    host = os.environ["db_host"]
    port = os.environ["db_port"]
    db_name = os.environ["db_name"]
    user = os.environ["db_user"]
    password = os.environ["db_password"]
    conn_url = f'{user}:{password}@{host}:{port}/{db_name}'
    return conn_url