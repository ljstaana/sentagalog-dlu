from app import db

class User(db.Model): 
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=True) 
    first_name = db.Column(db.String(120), index=True)
    last_name = db.Column(db.String(120), index=True)

    def __repr__(self): 
        return '<User {}>'.format(self.username)

class Tweet(db.Model): 
    __tablename__ = "tweets"
    instance_id = db.Column(db.Integer, primary_key=True, index=True)
    tweet_id = db.Column(db.String(128))
    author = db.Column(db.String(64)) 
    text = db.Column(db.String(460)) 
    created_at = db.Column(db.String(256)) 
    language = db.Column(db.String(15)) 
    search_term = db.Column(db.String(64)) 
    dataset_domain = db.Column(db.String(64))
    sentiment = db.Column(db.Integer) 
    labeller = db.Column(db.Integer)
    reason_for_sentiment = db.Column(db.String(64))


class LabelHistory(db.Model):
    __tablename__ = "label_history"
    import datetime
    label_id = db.Column(db.Integer, primary_key=True, index=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer) 
    tweet_id = db.Column(db.Integer)
    sentiment = db.Column(db.Integer)
    reason_for_sentiment = db.Column(db.String(128))