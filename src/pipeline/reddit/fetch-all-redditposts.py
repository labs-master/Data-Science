import praw
import os
import time
from multiprocessing import Pool, Process
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, inspect
from .database.tables import RedditPost,pg_utcnow

HOST = os.environ['PG_HOSTNAME']
PORT = os.environ['PG_PORT']
USER = os.environ['PG_USERNAME']
PASS = os.environ['PG_PASSWORD']
TABLE = 'reddit_posts'
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']

REDDIT = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# for lambda function pass these args : (event, context)
def handler():
    postgres_params = dict(
        drivername='postgres',
        username=USER,
        password=PASS,
        host=HOST,
        port=PORT
    )
    url = URL(**postgres_params).__to_string__()
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # might delete this later
    if TABLE not in inspect(engine).get_table_names():
        reddit_posts = RedditPost().create(engine)

    # could add custom sleep here?
    # or how would we execute every hour?
    # check below for a really janky way of terminating
    for comment in reddit.subreddit('all').stream.comments():
        reddit_post = RedditPost(
            text=comment.body,
            time=comment.created_utc,
            timestamp=pg_utcnow(),
            subreddit_id=comment.subreddit_id
        )
        session.add(reddit_post)
        session.commit()

if __name__ == '__main__':

    func = multiprocessing.Process(target=handler, name="Add new Reddit posts", args=())
    func.start()
    # run for 10 minutes then stop
    time.sleep(600)
    if func.is_alive():
        func.terminate()
        func.join()

