from app import app
from flask import Flask, session, render_template, url_for, request, redirect

ADMIN = 1
VOLUNTEER = 2

# / - splash screen
@app.route('/')
def splash():
    if "username" in session: 
        return redirect(url_for("dashboard"))
    return render_template('splash.html')

# / - login action 
@app.route('/login', methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    from app.models import User
    user = User.query\
               .filter_by(username=username, password=password)\
               .all()
    print(user)
    if len(user) == 1:
        session["username"] = user[0].username
        session["role"] = user[0].role
    return {
        "user" : [username]
    }

# / - logout action 
@app.route('/logout')
def logout(): 
    session.pop("username", None)
    return redirect(url_for("splash"))

# /dashboard - app dashboard
@app.route("/dashboard")
def dashboard(): 
    if 'username' in session:
        return render_template('dashboard.html', 
            username=session["username"],
            session=session)
    else: 
        return render_template('splash.html')

# /view_dataset - view dataset 
@app.route("/view_dataset")
def view_dataset(): 
    if 'username' in session:
        return render_template('view_dataset.html', 
            username=session["username"],
            session=session)
    else: 
        return render_template('splash.html')

# /view_tweets - view tweets 
@app.route("/view_tweets", methods=["POST"])
def view_tweets():
    if 'username' in session:
        from app.models import Tweet
        from sqlalchemy import desc, asc
        from app import db
        data = request.json 
        print(data)
        results = {}
        field = data["field"]
        like = data["filter"]
        ord_field = data["ord_field"]
        ord_dir = data["ord_dir"]
        limit = data["limit"]
        offset = (int(data["offset"]) - 1) * limit

        order = None 
        if ord_dir == "DESC": 
            order = desc(getattr(Tweet, ord_field))
        else: 
            order = asc(getattr(Tweet, ord_field))

        header = Tweet.query 

        if len(like) > 0:
            header = header.filter(getattr(Tweet, field).like("%" + like + "%"))

        results = header.order_by(order)\
                             .limit(limit).offset(offset)\
                             .all()

        ntweets = None
        if len(like) > 0:
            ntweets = db.session.query(Tweet)\
                        .filter(getattr(Tweet, field).like("%" + like + "%"))\
                        .count()    
        else: 
            ntweets = db.session.query(Tweet)\
                        .count()
        
        return {
            "tweets" : [
                [result.author, result.text, 
                 result.created_at, result.language, 
                 result.search_term, result.dataset_domain, 
                 result.sentiment, result.labeller, 
                 result.reason_for_sentiment, result.tweet_id] 
                for result in results
            ], 
            "ntweets" : ntweets
        }
    else: 
        return "You must be logged in to do that."

# /view_charts_and_stats - view charts and other statistics
@app.route("/view_charts_stats")
def view_charts_and_stats(): 
    if 'username' in session: 
        from app.models import Tweet
        from app.models import User 
        return render_template("view_charts_and_stats.html",
                username=session["username"],
                session=session
        )
    else: 
        return render_template("splash.html")

# /label_random_tweet - label a random tweet 
@app.route("/label_random_tweet")
def label_random_tweet(): 
    if 'username' in session: 
        from app.models import Tweet 
        from app.models import User 
        return render_template("label_random_tweet.html",
            username=session["username"],
            session=session
        )
    else: 
        return render_template("splash.html")


# /label_specific_tweet - label a specific tweet
@app.route("/label_specific_tweet")
def label_specific_tweet(): 
    if 'username' in session: 
        from app.models import Tweet 
        from app.models import User 
        tweet_id = request.args.get("tweet_id")
        return render_template("label_specific_tweet.html",
            username=session["username"],
            tweet_id=tweet_id,
            session=session) 
    else: 
        return render_template("splash.html")


# /label_history - view the label history
@app.route("/label_history")
def view_label_history(): 
    if 'username' in session: 
        from app.models import LabelHistory 
        from app.models import Tweet 
        from app.models import User
        from app import db

        username = session["username"]
        user_id = User.query.filter_by(username=username).first().id
        limit = request.args.get("limit", 10)
        page = int(request.args.get("page", 1)) - 1
        offset = page * limit 
        order_by = request.args.get("order_by", "created_date") 
        order_dir = request.args.get("order_dir", "desc")

        order = None 
        if order_dir == "desc":
            order = getattr(LabelHistory, order_by).desc() 
        else: 
            order = getattr(LabelHistory, order_by).asc()
        

        label_logs = db.session.query(LabelHistory)\
                        .order_by(order)\
                        .limit(limit)\
                        .offset(offset).all()
        
        total = db.session.query(LabelHistory).count()

        for label in label_logs: 
            label.username = User.query.filter_by(id=label.user_id).first().username
            text = db.session.query(Tweet)\
                    .filter_by(tweet_id=label.tweet_id)\
                    .first().text 
            label.text = text


        for label in label_logs: 
            label.username = username 
            text = db.session.query(Tweet)\
                     .filter_by(tweet_id=label.tweet_id)\
                     .first().text 
            label.tweet_text = text

        return render_template("label_history.html", 
            username=session["username"],
            label_logs=label_logs, 
            limit=limit, 
            page=page, 
            offset=offset, 
            total=total,
            session=session)
    else: 
        return render_template("splash.html")

# /my_labels -  lets the user view his or her labels 
@app.route("/my_labels")
def my_labels(): 
    if 'username' in session: 
        from app.models import LabelHistory 
        from app.models import Tweet 
        from app.models import User
        from app import db 
        
        username = session["username"]
        user_id = User.query.filter_by(username=username).first().id
        limit = request.args.get("limit", 10)
        page = int(request.args.get("page", 1)) - 1 
        offset = page * limit 
        order_by = request.args.get("order_by", "created_date")
        order_dir = request.args.get("order_dir", "desc") 

        order = None 
        if order_dir ==  "desc" : 
            order = getattr(LabelHistory, order_by).desc() 
        else: 
            order = getattr(LabelHistory, order_by).desc() 

        label_logs = db.session.query(LabelHistory)\
                        .filter_by(user_id=user_id)\
                        .order_by(order)\
                        .limit(limit)\
                        .offset(offset).all()

        total = db.session.query(LabelHistory)\
                        .filter_by(user_id=user_id)\
                        .count() 
       
        for label in label_logs: 
            label.username = username 
            text = db.session.query(Tweet)\
                     .filter_by(tweet_id=label.tweet_id)\
                     .first().text
         
            label.tweet_text = text

        return render_template("my_labels.html",
            username=session["username"], 
            label_logs=label_logs, 
            limit=limit,
            page=page, 
            offset=offset,
            total=total,
            session=session
        )
    else: 
        return render_template("splash.html")

@app.route("/create_user") 
def create_user():
    if 'username' in session:
        if session['role'] == 1: 
            return render_template("create_user.html",
                username=session["username"],
                session=session)
        else: 
            return "You are not permitted in this page. Sorry." 
    else: 
        return render_template("splash.html")


@app.route("/view_users")
def view_users(): 
    if 'username' in session: 
        from app.models import User 
        from app.models import Tweet
        from app import db
        users = db.session.query(User)\
                  .all() 
        
        
        for user in users: 
            nlabels = Tweet.query.filter_by(labeller=user.id).count()
            user.nlabels = nlabels 

        return render_template("view_users.html",
            username=session["username"],
            users=users,
            session=session
        )
    else: 
        return render_template("splash.html")

# ------------------ API FUNCTIONS ----------------- #

# /api/label_status - label status of the tweets
@app.route("/api/label_status")
def api_label_status(): 
    if 'username' in session: 
        from app import db
        from app.models import Tweet 
        from app.models import User
        
        # count number of labelled and unlabelled tweets 
        total_tweets = db.session.query(Tweet).count()
        labelled_tweets = db.session.query(Tweet).filter(getattr(Tweet, "sentiment").isnot(None)).count() 
        unlabelled_tweets = total_tweets - labelled_tweets
        discard_tweets = db.session.query(Tweet).filter(getattr(Tweet, "sentiment").is_(-2)).count()
        sarcasm_tweets = db.session.query(Tweet).filter(getattr(Tweet, "sentiment").is_(2)).count()


        # breakdown of sentiment labels
        positive_tweets = db.session.query(Tweet).filter_by(sentiment=1).count() 
        negative_tweets = db.session.query(Tweet).filter_by(sentiment=-1).count() 
        neutral_tweets = db.session.query(Tweet).filter_by(sentiment=0).count() 
    
        # labelled by term
        positive_tweets_by_term = \
            db.session.query(Tweet.search_term, db.func.count(Tweet.sentiment))\
              .filter_by(sentiment=1).group_by(Tweet.search_term).all() 
        negative_tweets_by_term = \
            db.session.query(Tweet.search_term, db.func.count(Tweet.sentiment))\
              .filter_by(sentiment=-1).group_by(Tweet.search_term).all() 
        neutral_tweets_by_term = \
            db.session.query(Tweet.search_term, db.func.count(Tweet.sentiment))\
              .filter_by(sentiment=0).group_by(Tweet.search_term).all()

        # labelled by language 
        positive_tweets_by_language = \
            db.session.query(Tweet.language, db.func.count(Tweet.sentiment))\
              .filter_by(sentiment=1).group_by(Tweet.language).all() 
        negative_tweets_by_language = \
            db.session.query(Tweet.language, db.func.count(Tweet.sentiment))\
              .filter_by(sentiment=-1).group_by(Tweet.language).all() 
        neutral_tweets_by_language = \
            db.session.query(Tweet.language, db.func.count(Tweet.sentiment))\
              .filter_by(sentiment=0).group_by(Tweet.language).all() 

        # no of labels per user 
        users = User.query.all()
        label_counts = {}
        for user in users:
            id = user.id 
            username = user.username 
            label_counts[username] = \
                Tweet.query.filter_by(labeller=id).count()
        

        
        payload = {
            "by_language" : {
                "positive" : dict(positive_tweets_by_language), 
                "negative" : dict(negative_tweets_by_language), 
                "neutral" : dict(neutral_tweets_by_language) 
            }, 
            "by_term" : {
                "positive" : dict(positive_tweets_by_term), 
                "negative" : dict(negative_tweets_by_term), 
                "neutral" :  dict(neutral_tweets_by_term)
            }, 
            "all" : {
                "positive" :  positive_tweets, 
                "negative" :  negative_tweets, 
                "neutral" :   neutral_tweets
            }, 
            "meta" : {
                "unlabelled" : unlabelled_tweets, 
                "labelled" :   labelled_tweets, 
                "total" :      total_tweets, 
                "discards" : discard_tweets, 
                "sarcasms" : sarcasm_tweets
            },
            "label_counts" : label_counts
        }


        return payload

@app.route("/api/get_random_unlabelled_tweet")
def api_get_random_tweet(): 
    if 'username' in session: 
        from app import db 
        from app.models import Tweet 
        
        result = Tweet.query.filter(getattr(Tweet, "sentiment").is_(None)).order_by(db.func.random()).first()
        reasons = Tweet.query.group_by(Tweet.reason_for_sentiment).all()
        reasons = [res.reason_for_sentiment for res in reasons]
        reasons.remove(None)

        print(reasons)

        return { 
            "tweet" : [
                result.tweet_id, 
                result.author, 
                result.text, 
                result.search_term, 
                result.dataset_domain
            ], 
            "reasons" : reasons
        }


@app.route("/api/get_specific_tweet")
def api_get_specific_tweet(): 
    if 'username' in session: 
        from app import db 
        from app.models import Tweet 
        id = request.args.get("tweet_id", None)
        
        
        result = Tweet.query.filter(getattr(Tweet, "tweet_id").is_(id)).all()
        reasons = Tweet.query.group_by(Tweet.reason_for_sentiment).all()
        reasons = [res.reason_for_sentiment for res in reasons]
        reasons.remove(None)

        if(len(result) == 0):
            return "No tweet found"
        else: 
            return  { 
            "tweet" : [
                result[0].tweet_id,
                result[0].author, 
                result[0].text, 
                result[0].search_term, 
                result[0].dataset_domain
            ], 
            "reasons" : reasons
        }


@app.route("/api/submit_label", methods=["POST"])
def api_submit_label(): 
    if 'username' in session: 
        from app import db 
        from app.models import Tweet 
        from app.models import LabelHistory 
        from app.models import User 
        username = session["username"]
        user_id = User.query.filter_by(username=username).first().id
        sentiment = request.json["sentiment"]
        reason_for_sentiment = request.json["reason_for_sentiment"]
        tweet_id = request.json["tweet_id"] 
        print((username, user_id, sentiment, reason_for_sentiment, tweet_id))

        tweet = Tweet.query.filter_by(tweet_id=tweet_id).first()
        tweet.sentiment = sentiment 
        tweet.reason_for_sentiment = reason_for_sentiment 
        tweet.labeller = user_id

        label_history = LabelHistory(user_id=user_id, sentiment=sentiment,
                                     reason_for_sentiment=reason_for_sentiment,
                                     tweet_id=tweet_id)

        try:
            db.session.add(label_history)
            db.session.add(tweet)
            db.session.commit()
            return {
                "state" : "successful"
            }
        except E: 
            return {
                "state" : "unsuccessful"
            }


@app.route("/api/create_user", methods=["POST"])
def api_create_user(): 
    if 'username' in session: 
        if session['role'] == ADMIN:  
            from app import db 
            from app.models import User 
            user = request.json.get('user', {})
            new_user = User(
                username=user["username"], 
                first_name=user["first_name"], 
                last_name=user["last_name"], 
                password=user["password"], 
                role=user["role"]
            )
            db.session.add(new_user)
            db.session.commit()

            return "success"
        else: 
            return "You are not allowed to access this resource."
    else: 
        return "You are not allowed to access this resource."

@app.route("/api/delete_user", methods=["POST"]) 
def api_delete_user(): 
    if 'username' in session: 
        if session['role'] == ADMIN:
            from app import db 
            from app.models import User
            user_id = request.json.get("id") 
            User.delete.filter_by(user_id=user_id)
            return "success"
        else: 
            return "You are not allowed to access this resource."
    else: 
        return "You are not allowed to access this resource"