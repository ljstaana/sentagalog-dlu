from app import db
from app.models import Tweet
import pandas as pd
datafile = "deep_filtered.csv"

data = pd.read_csv(datafile)

for index, row in data.iterrows(): 
    print("Processing " + str(index) + " of " + str(len(data)) + " tweets.")
    tweet = Tweet()
    tweet.tweet_id = row["id"]
    tweet.author = row["author"]
    tweet.text = row["text"]
    tweet.created_at = row["created_at"]
    tweet.language = row["language"]
    tweet.search_term = row["search_term"]
    tweet.dataset_domain = row["dataset_domain"]
    db.session.add(tweet)

print("Committing.")
db.session.commit()
print("Successfuly committed...")