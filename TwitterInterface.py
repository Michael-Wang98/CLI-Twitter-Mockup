import sqlalchemy as db
import pymysql
import cryptography
from os import sys

#################################################


# Add a method to shorten the code needed to execute a query
def query(q):
    return connection.execute(q)


# Method to count elements, if 0 optional arguments count entries in table,
# if 1 then count entries where column = threshold,
# if 4 then count entries in table where a column = threshold and a second column = threshold2
def count(column, threshold="UNUSED", column2="UNUSED", threshold2="UNUSED"):
    if threshold == "UNUSED":
        return db.select([db.func.count(column)])
    elif column2 == "UNUSED":
        return db.select([db.func.count(column)]).where(column == threshold)
    return db.select([db.func.count(column)]).where(db.and_(column == threshold, column2 == threshold2))


# Method that adds a follow entry to followPeople if what is p and to followTopic otherwise of the user and receiver
def follow(what, user, receive):
    if what == "p":
        return db.insert(followPeople).values(follower=user, receiver=receive)
    else:
        return db.insert(followTopic).values(follower=user, fTopic=receive)


# Method that determines if a post is older or newer than the previous session
def newer(tweet, lastYear, lastMonth, lastDay):
    year = query(select(tweets.columns.post_year, tweets.columns.tweetID, tweet))
    for i in year:
        i = str(i).replace(",)", "").replace("(", "")
        if int(lastYear) < int(i):
            return True
    month = query(select(tweets.columns.post_month, tweets.columns.tweetID, tweet))
    for i in month:
        i = str(i).replace(",)", "").replace("(", "")
        if int(lastMonth) < int(i):
            return True
    day = query(select(tweets.columns.post_day, tweets.columns.tweetID, tweet))
    for i in day:
        i = str(i).replace(",)", "").replace("(", "")
        if int(lastDay) < int(i):
            return True
    return False


# Method that adds a post to the tweets table with most fields blank given that they're mostly analytical fields a user
# wouldn't have control over anyways. The fields that are filled are a uniquely generated tweetID, post topic, poster's
# username, initializing the retweet and likes fields to 0 and finally the tweet text
def post(tid, ttopic, tuser, ttext):
    return db.insert(tweets).values(tweetID=tid,
                                    airline_sentiment="",
                                    airline_sentiment_confidence=0,
                                    negativereason="",
                                    negativereason_confidence=0,
                                    topic=ttopic,
                                    airline_sentiment_gold="",
                                    userName=tuser,
                                    negativereason_gold="",
                                    retweet_count=0,
                                    likes=0,
                                    tweetText=ttext)


# Adds an entry to the response table
def respond(orig, resp):
    return db.insert(responses).values(original=orig, response=resp)


# A method to reduce code necessary for a select query, with no optional arguments equivalent to a simple SELECT * and
# with the optional arguments is SELECT * with a WHERE clause
def select(criteria, where="UNUSED", threshold="UNUSED"):
    if where == "UNUSED":
        return db.select([criteria])
    return db.select([criteria]).where(where == threshold)


# updates the tweets database with a new likes or retweets value
def update(like, newLikes, match):
    if like == "l":
        return db.update(tweets).values(likes=newLikes).where(tweets.columns.tweetID == match)
    if like == "r":
        return db.update(tweets).values(retweet_count=newLikes).where(tweets.columns.tweetID == match)


# takes the result object and converts it to a string with the parenthesis and comma at the end removed
def result(raw):
    return str(raw.fetchall()[0]).replace(",)", "").replace("(", "")


#################################################

# database credentials
username = ''
password = ''
hostname = 'localhost'
database = 'twitter'

# establish connection to mysql database
engine_string = "mysql+pymysql://"+username+":"+password+"@"+hostname+":"+"3306"+"/"+database
try:
    engine = db.create_engine(engine_string)
    connection = engine.connect()
    print("Successfully connected to: " + database)
except Exception as e:
    print("Error connecting to MySQL DB: " + str(e))
    sys.exit()

#################################################

# Load in the metadata and all the tables in the twitterDB database
metadata = db.MetaData()
tweets = db.Table('tweets', metadata, autoload=True, autoload_with=engine)
followPeople = db.Table('followPeople', metadata, autoload=True, autoload_with=engine)
followTopic = db.Table('followTopic', metadata, autoload=True, autoload_with=engine)
responses = db.Table('responses', metadata, autoload=True, autoload_with=engine)
topics = db.Table('topics', metadata, autoload=True, autoload_with=engine)
users = db.Table('users', metadata, autoload=True, autoload_with=engine)

#################################################

username = input("please enter your username: ")
ongoing = True  # Variable to control the main loop

# Checks if username is in the users table and requests reentry of username until a registered username is entered
while result(query(count(users.columns.userName, username))) == "0":
    print("\nThat is not a registered username\n")
    username = input("please enter your username: ")

# Generate unique tweetIDs using tweet table size
tweetid = int(result(query(count(tweets.columns.tweetID))))+600000000000000000

print("\nWelcome " + username + "\n")
options = ["Post", "Follow another user", "Follow a Topic", "Like or dislike a post", "Retweet", "Inspect a post", "exit"]
for x in options:
    print("Press " + str(options.index(x)+1) + " to " + x)

# Main loop which will repeat until the user is done
while ongoing:
    action = input("What would you like to do? ")

    # Tweet, if the topic the user wants to post to isn't in the topic table it will prompt them to create it or be
    # returned to the main loop. Then ask them to compose a tweet in 280 characters or less using a slice to keep it in
    # character limit. Then asks if the tweet is a response to another tweet, if so then ask what tweet they are
    # responding to and adds an entry to the response table accordingly. Increment the tweetID value for the session.
    if action == "1":
        fail = False
        topic = input("what topic would you like to post to: ")
        if result(query(count(topics.columns.topic, topic))) == "0":
            newTopic = input("That is not currently a topic would you like to create it (y/n): ")
            if newTopic == "y":
                query(db.insert(topics).values(topic=topic))
                print("New topic created: " + topic)
            else:
                fail = True

        if not fail:
            tweettext = input("Enter your tweet in 280 characters or less: ")[0:279]  # Slice first 280 chars to enforce limit

            query(post(tweetid, topic, username, tweettext))

            response = input("Is this a response to another post (y/n): ")
            if response == "y":
                responseID = input("Enter the tweetID of the tweet being responded to: ")
                if result(query(count(tweets.columns.tweetID, responseID))) == "0":
                    print("That is not a valid tweetID")
                else:
                    query(respond(int(responseID), tweetid))
                    print("Responded")
            print("Thanks for making your opinion heard\n")
            tweetid += 1

    # Follow another user by username. If the username is not in the users table put them back in the main loop, if they
    # are already following that person put them back in the main loop. If neither of the above is true then add an
    # entry to the followPeople table
    elif action == "2":
        receiver = input("Who would you like to follow: ")
        if result(query(count(users.columns.userName, receiver))) == "0":
            print("That is not a registered user\n")
        elif result(query(count(followPeople.columns.follower, username, followPeople.columns.receiver, receiver))) == "1":
            print("You are already following that user\n")
        else:
            query(follow("p", username, receiver))
            print("You are now following " + receiver + "\n")

    # Follow a topic by name. If the topic is not in the topic table put them back in the main loop, if they
    # are already following that person put them back in the main loop. If neither of the above is true then add an
    # entry to the followTopic table. If the user wishes to create a topic it must be done by posting.
    elif action == "3":
        topic = input("What topic would you like to follow: ")
        if result(query(count(topics.columns.topic, topic))) == "0":
            print("That is not a topic, if you would like to create that topic tweet @ it\n")
        elif result(query(count(followTopic.columns.follower, username, followTopic.columns.fTopic, topic))) == "1":
            print("You are already following that topic\n")
        else:
            query(follow("t", username, topic))
            print("You are now following " + topic + "\n")

    # Like or dislike a tweet by tweetID. If the tweetID is not in the tweet table put them back in the main loop.
    # Otherwise ask them if they'd like to like or dislike the tweet. Increment or decrement that tweet's likes or
    # dislikes accordingly
    elif action == "4":
        ltweet = input("Which post would you like to react to: ")
        if result(query(count(tweets.columns.tweetID, ltweet))) == "1":
            currentLikes = int(result(query(select(tweets.columns.likes, tweets.columns.tweetID, ltweet))))
            like = input("Like the tweet (y/n): ")
            if like == 'y':
                query(update("l", currentLikes+1, ltweet))
                print("Liked")
            else:
                query(update("l", currentLikes-1, ltweet))
                print("Disliked")
        else:
            print("That is not a valid tweetID")

    # Retweet a tweet by tweetID. If the tweetID is not in the tweet table put them back in the main loop.
    # Otherwise increment that tweet's retweets
    elif action == "5":
        ltweet = input("Which post would you like to retweet: ")
        if result(query(count(tweets.columns.tweetID, ltweet))) == "1":
            currentLikes = int(result(query(select(tweets.columns.retweet_count, tweets.columns.tweetID, ltweet))))
            query(update("r", currentLikes+1, ltweet))
            print("Retweeted")
        else:
            print("That is not a valid tweetID")

    # Inspect a tweet by tweetID. If the tweetID is not in the tweet table put them back in the main loop. Otherwise,
    # print out the attributes of the tweet requested.
    elif action == "6":
        inspect = input("Which tweet would you like to inspect: ")
        if result(query(count(tweets.columns.tweetID, inspect))) == "1":
            print(query(select(tweets, tweets.columns.tweetID, inspect)).fetchall()[0])
        else:
            print("That is not a valid tweetID")

    # Check for unread tweets by people and topics being followed. Any tweet newer than the last time the user signed in
    # is considered unread for the purpose of this social network. Gather a list of topics and people this user is
    # following and then display all tweets made by those people and topics made after the last time they signed in
    elif action == "7":
        newPosts = []
        ftopics = query(select(followTopic.columns.fTopic, followTopic.columns.follower, username))
        fpeople = query(select(followPeople.columns.receiver, followPeople.columns.follower, username))
        year = input("What year did you last sign in?")
        month = input("Which month was it?")
        day = input("Which day was it?")
        for a in ftopics:
            a = str(a).replace("',)", "").replace("('", "")
            temp = query(select(tweets.columns.tweetID, tweets.columns.topic, a))
            for b in temp:
                b = int(str(b).replace(",)", "").replace("(", ""))
                duplicate = False
                for c in newPosts:
                    if b == c:  # Make sure not to duplicate tweets displayed by ensuring the tweet isn't already gotten
                        duplicate = True
                        break
                if not duplicate:
                    if newer(b, year, month, day):
                        newPosts.append(b)

        for a in fpeople:
            a = str(a).replace("',)", "").replace("('", "")
            temp = query(select(tweets.columns.tweetID, tweets.columns.userName, a))
            for b in temp:
                b = int(str(b).replace(",)", "").replace("(", ""))
                duplicate = False
                for c in newPosts:
                    if b == c:  # Make sure not to duplicate tweets displayed by ensuring the tweet isn't already gotten
                        duplicate = True
                        break
                if not duplicate:
                    if newer(b, year, month, day):
                        newPosts.append(b)

        for unread in newPosts:
            print(unread)



    # Exit the program by ending the while loop
    elif action == "X":
        ongoing = False
