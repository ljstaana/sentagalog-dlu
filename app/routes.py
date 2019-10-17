from app import app
import json
from flask import Flask, session, render_template, url_for, request, redirect
from app.classes import UserClass, ReasonClass, TweetClass, LabelClass
from app.models import User, Tweet, Labels, Reason
from app import db
from sklearn.metrics import cohen_kappa_score

ADMIN = 1
VOLUNTEER = 2

NEGATIVE = 0 
NEUTRAL = 1 
POSITIVE = 2 
SARCASM = 3 
DISCARD = 4

sent_names = {
    0 : "negative", 
    1 : "neutral", 
    2 : "positive", 
    3 : "sarcasm", 
    4 : "discard"
}

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
    else :
        return {}

# / - logout action 
@app.route('/logout')
def logout(): 
    session.pop("username", None)
    return redirect(url_for("splash"))

# ------------ APPLICATION DASHBOARD ------------ #

# /dashboard - app dashboard
@app.route("/dashboard")
def dashboard(): 
    if 'username' in session:
        return render_template('dashboard.html', 
            user=UserClass.get_user(session["username"]),
            session=session)
    else: 
        return render_template('splash.html')

# ----------------- USERS ------------------------# 

# USER PROFILE  
# -----------------------------------------------
# /profile - user profile 
@app.route("/profile") 
def profile(): 
    if 'username' in session: 
        return render_template('profile.html', 
            user=UserClass.get_user(session["username"]), 
            session=session) 
    else: 
        return render_template('splash.html')

# /edit_profile - page to edit user profile
@app.route("/edit_profile")
def edit_profile(): 
    if 'username' in session: 
        return render_template('edit_profile.html', 
            user=UserClass.get_user(session["username"]), 
            session=session)
    else: 
        return render_template('splash.html')

# /edit_profile_next - updates profile information
@app.route("/edit_profile_next", methods=["POST"])
def edit_profile_next(): 
    if 'username' in session: 
        action = request.json.get("action")
        data = request.json.get("data")
        user_id = User.query.filter_by(username=session["username"])[0].id
        if action == "update_account_information": 
            target_user = User.query.filter_by(id=user_id).all()[0]
            target_user.username = data["username"]
            target_user.first_name = data["first_name"] 
            target_user.last_name = data["last_name"]
            target_user.bio = data["bio"]
            target_user.avatar = data["avatar"] 
            db.session.add(target_user)
            db.session.commit()
        return data
    else: 
        return "You are not allowed to access this resource."

# /verify_password - verifies if a payload password matches the current password
# of the user that is logged in
@app.route("/change_password", methods=["POST"])
def change_password():
    if 'username' in session: 
        current_password = request.json.get("current_password")
        new_password = request.json.get("new_password")
        confirm_password = request.json.get('confirm_new_password')
        
        user = User.query.filter_by(username=session["username"]).all()[0]
        user_password = user.password

        if current_password == user_password: 
            if new_password == confirm_password:
                user.password = new_password 
                db.session.add(user)
                db.session.commit()
                return {
                    "result" : "Successfully updated passwords", 
                    "type" : "success"
                }
            else: 
                return {
                    "result" : "New passwords do not match.", 
                    "type" : "error"
                }
        else: 
            return {
                "result": "Wrong current password.",
                "type" : "error"
            }
    else: 
        return "You are not allowed to access this resource."


# /users - lists down details of all users 
@app.route("/users")
def users(): 
    if 'username' in session: 
        users = User.query.order_by(User.role.desc()).all()
        return render_template("users.html", 
            users = users, 
            user = UserClass.get_user(session["username"]),
            session = session
        )
    else: 
        return "You are not allowed to access this resource."

# --------------------- DATASET ------------------------# 

# /view_tweets - a timeline like display of all the tweets 
# together with attached labels from the two raters
@app.route("/view_tweets")
def view_tweets(): 
    if 'username' in session:
        page = request.args.get("page", "1") 
        page_size = 10
        query = Tweet.query
        qstr = request.args.get("q", "")
        print(qstr)
        dq = query
        if len(qstr) > 0:
            middle = Tweet.text.like('% '+qstr+' %') 
            first = Tweet.text.like(qstr+' %')
            last = Tweet.text.like(qstr+' %')

            from sqlalchemy import or_
            query = query.filter(or_(middle, first, last))
            dq = query
        
        query = query.order_by(Tweet.author.asc())

        if page_size: 
            query = query.limit(page_size) 
        if page: 
            query = query.offset((int(page)-1)*page_size)

    
        tweets = query.all()
        tweet_count = dq.count()

        return render_template("view_tweets.html",
            qstr = qstr, 
            tweets = tweets, 
            tweet_count = tweet_count,
            user = UserClass.get_user(session["username"]), 
            session = session,
            page = page
        )
    else: 
        return "You are not allowed to access this resource"


# /label_tweets - allows the user to label a specific tweet
@app.route("/label_tweets")
def label_tweets(): 
    if 'username' in session:
        return render_template("label_tweets.html", 
            user = UserClass.get_user(session["username"]), 
            session = session
        )
    else: 
        return "You are not allowed to access this resource"


@app.route("/label_tweets/tweet_to_label")
def label_tweets_get_to_label(): 
    if 'username' in session:
        tweet = UserClass.get_tweet_to_label(session["username"]) 
        id = tweet.instance_id 
        text = tweet.text
        author = tweet.author
        return {
            "id" : id, 
            "text" : text, 
            "author" : author
        }
    else: 
        return "You are not allowed to access this resource"

@app.route("/label_tweets/reasons")
def label_tweets_reasons(): 
    if 'username' in session: 
        reasons = Reason.query.all() 
        reasons_list = [] 
        for reason in reasons: 
            reasons_list.append({
                "id" : reason.reason_id, 
                "reason" : reason.reason
            })
        return json.dumps(reasons_list)
    else:
        return "You are not allowed to access this resource"


@app.route("/label_tweets/label", methods=["POST"])
def label_tweets_label(): 
    if 'username' in session:
        username = session["username"]
        id = request.json.get("id")
        reason = request.json.get("reason")
        new = request.json.get("new") 
        sentiment = request.json.get("sentiment")

        # get the user id of the current user 
        user = User.query.filter_by(username=username).all()[0]
        user_id = user.id

        # retrieve the sentiment code of the current 
        # sentiment 
        sent_code = -1
        if sentiment == "negative": 
            sent_code = NEGATIVE 
        elif sentiment == "neutral":
            sent_code = NEUTRAL 
        elif sentiment == "positive":
            sent_code = POSITIVE
        elif sentiment == "sarcasm":
            sent_code = SARCASM 
        elif sentiment == "discard":
            sent_code = DISCARD

        print(request.json)
        print("Sent. Code: " + str(sent_code))

        # if reason is a new reason add it to the
        # reasons table 
        if new: 
            new_reason = Reason() 
            new_reason.reason = reason 
            new_reason.description = "To be described"

            db.session.add(new_reason)
            db.session.commit() 

        # retrieve the reason code 
        # of the current reason for sentiment
        reason = Reason.query.filter_by(reason=reason)
        reason_id = reason.all()[0].reason_id 
        print("Reason Code: " + str(int(reason_id))) 

 
        label = Labels()
        label.tweet_id = id 
        label.user_id = user_id
        label.sentiment = sent_code 
        label.reason_for_sentiment = reason_id 

        db.session.add(label)
        db.session.commit()
        
        # update the last labelled idx of user 
        user.last_labelled_id +=1 
        db.session.add(user)
        db.session.commit()
        
        return {
            "state" : "successful",
            "label_count" : user.last_labelled_id
        }
    else: 
        return "You are not allowed to access this resource"



@app.route("/label_tweets/edit_label_x", methods=["POST"])
def label_tweets_edit_label(): 
    if 'username' in session:
        username = session["username"]
        id = request.json.get("id")
        reason = request.json.get("reason")
        new = request.json.get("new") 
        sentiment = request.json.get("sentiment")

        # get the user id of the current user 
        user = User.query.filter_by(username=username).all()[0]
        user_id = user.id

        # retrieve the sentiment code of the current 
        # sentiment 
        sent_code = -1
        if sentiment == "negative": 
            sent_code = NEGATIVE 
        elif sentiment == "neutral":
            sent_code = NEUTRAL 
        elif sentiment == "positive":
            sent_code = POSITIVE
        elif sentiment == "sarcasm":
            sent_code = SARCASM 
        elif sentiment == "discard":
            sent_code = DISCARD

        print(request.json)
        print("Sent. Code: " + str(sent_code))

        # if reason is a new reason add it to the
        # reasons table 
        if new: 
            new_reason = Reason() 
            new_reason.reason = reason 
            new_reason.description = "To be described"

            db.session.add(new_reason)
            db.session.commit() 

        # retrieve the reason code 
        # of the current reason for sentiment
        reason = Reason.query.filter_by(reason=reason)
        reason_id = reason.all()[0].reason_id 
        print("Reason Code: " + str(int(reason_id))) 

        label = Labels.query.filter_by(user_id=user_id,tweet_id=id).all()[0]
        label.user_id = user_id
        label.sentiment = sent_code 
        label.reason_for_sentiment = reason_id
        db.session.add(label)
        db.session.commit()

    
        
        return {
            "state" : "successful",
            "label_count" : user.last_labelled_id
        }
     
        
        return {
            "state" : "successful",
            "label_count" : user.last_labelled_id
        }
    else: 
        return "You are not allowed to access this resource"


@app.route("/my_labels")
def my_labels(): 
    if 'username' in session: 
        return render_template("my_labels.html", 
            user = UserClass.get_user(session["username"]),
            session = session
        )
    else: 
        return "You are not allowed to access this resource"

@app.route("/my_labels/get_labels")
def my_labels_get_labels(): 
    if 'username' in session: 
        username = session['username']
        user = User.query.filter_by(username=username).all()[0]
        user_id = user.id 
        limit = 5
        page = int(request.args.get("page", 1)) - 1
        labels = Labels.query.filter_by(user_id=user_id) 
        label_count = labels.count()
        labels = labels.limit(limit)
        labels = labels.offset(page*limit) 

        
        labels_ = [] 
        for label in labels: 
            label_dict = {
                "user_id" : label.user_id, 
                "instance_id" : label.tweet_id, 
                "tweet" : TweetClass.get_tweet_dict(label.tweet_id),
                "sentiment" : int(label.sentiment), 
                "reason_for_sentiment" : label.reason_for_sentiment, 
                "created_at" : label.created_at , 
                "updated_at" : label.updated_at
            }
            labels_.append(label_dict)

        sentiments_ = sent_names 
        reasons_ = ReasonClass.get_reasons()

        pload = {
            "labels" : labels_, 
            "sentiments" : sentiments_, 
            "reasons" : reasons_, 
            "label_count" : label_count,
            "page" : page + 1
        }


        return pload

    else: 
        return "You are not allowed to access this resource"


@app.route("/edit_label")
def edit_label():
    if 'username' in session: 
        id = request.args.get("id")
        tweet = Tweet.query.filter_by(instance_id=id).all()[0]
        text = tweet.text
        author = tweet.author
        

        return render_template("edit_label.html", 
            user = UserClass.get_user(session["username"]), 
            session = session,
            id = id, 
            author = author, 
            text = text
        )
    else: 
        return "You are not allowed to access this resource"


@app.route("/number_stats")
def number_stats(): 
    if 'username' in session: 
        all_labels = Labels.query.all() 
        
        ID = 0 
        SENTIMENT = 1
        USER = 2

        # TALLIES
        tally_by_user = {
            1: {}, 
            2: {}
        } 
        for label in all_labels:
            tally_by_user[label.user_id][label.tweet_id] = label.sentiment 

        # COHEN'S KAPPA
        minv = min([len(tally_by_user[1]), len(tally_by_user[2])])
        y1 = list(tally_by_user[1].values())[0:minv]
        y2 = list(tally_by_user[2].values())[0:minv]
        kappa = cohen_kappa_score(y1, y2)
        
        label_counts = {
            1 : len(tally_by_user[1]), 
            2 : len(tally_by_user[2])
        }

        import pprint as pp

        # CONFUSION MATRIX
        cm = LabelClass.confusion_matrix(y1, y2)
        pp.pprint(cm)

        return render_template("number_stats.html", 
            user = UserClass.get_user(session["username"]), 
            session = session,
            label_counts = label_counts,
            kappa = kappa, 
            kappa_count = minv,
            cm = cm,
            names = list(sent_names.values())
        )
    else: 
        return "You are not allowed to access this resource"


@app.route("/charts")
def charts(): 
    if 'username' in session: 
        return render_template("charts.html", 
            user = UserClass.get_user(session["username"]), 
            session = session
        )
    else: 
        return "You are not allowed to access this resource"