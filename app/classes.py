from app import db 
from app.models import User, Tweet, Reason

class TweetClass: 

    @staticmethod 
    def get_tweets(): 
        tweets = Tweet.query.order_by(Tweet.author.asc()).all() 
        return tweets 

    @staticmethod 
    def get_tweet_offset(offset): 
        offset += 2
        query = Tweet.query.order_by(Tweet.author.asc())
        query = query.limit(10).offset(offset)
        return query.all()[0]

    
    @staticmethod 
    def get_sentiments(): 
        pass

    @staticmethod 
    def get_tweet_dict(instance_id):
        tweet = Tweet.query.filter_by(instance_id=instance_id).all()[0]
        instance_id = tweet.instance_id 
        author = tweet.author 
        text = tweet.text 
        created_at = tweet.created_at 
        language = tweet.language 
        search_term = tweet.search_term, 
        dataset_domain = tweet.dataset_domain 
        return {
            "instance_id" : instance_id, 
            "author" : author, 
            "text" : text, 
            "created_at" : created_at, 
            "language" : language, 
            "search_term" : search_term, 
            "dataset_domain" : dataset_domain
        }


class ReasonClass: 

    @staticmethod 
    def get_reasons(): 
        reasons_map = {} 
        reasons = Reason.query.all() 
        for reason in reasons: 
            reasons_map[reason.reason_id] = reason.reason 
        return reasons_map

class UserClass: 
    
    @staticmethod 
    def get_user(username): 
        user = User.query.filter_by(username=username).all() 
        user = user[0]
        
        username = user.username
        first_name = user.first_name 
        last_name = user.last_name
        avatar = user.avatar 
        role = user.role 
        bio = user.bio
        id = user.id
        last_labelled_id = user.last_labelled_id

        return {
            "username" : username, 
            "avatar" : avatar, 
            "first_name" : first_name,
            "last_name" : last_name, 
            "role" : role, 
            "bio" : bio,
            "last_labelled_id" : last_labelled_id
        }    
    
    @staticmethod 
    def get_tweet_to_label(username):
        user = User.query.filter_by(username=username).all()
        user = user[0]
        last_labelled_id = user.last_labelled_id 
        
        # retrieve tweet using offset 
        tweet_to_label = TweetClass.get_tweet_offset(last_labelled_id)
        
        return tweet_to_label

class LabelClass: 

    @staticmethod 
    def confusion_matrix(y1, y2):
        cm = []
        for i in range(5):
            cm.append([])
            for j in range(5): 
                cm[i].append(0) 

        import pprint as pp
        pp.pprint(cm) 
        
        for i in range(len(y1)):
            r1 = y1[i]
            r2 = y2[i] 
            # print("ROW: " + str(i))
            # print("Rater 1: " + str(r1))
            # print("Rater 2: " + str(r2))
            cm[r1][r2] += 1
        return cm