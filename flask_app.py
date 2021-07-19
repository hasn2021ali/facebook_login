import os

import flask
from flask import request, jsonify, render_template , session, redirect, url_for
from flask import json
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import sqlite3


# Your ngrok url, obtained after running "ngrok http 5000"
URL = "https://hasanali101.pythonanywhere.com"
 

FB_CLIENT_ID = "335582323665126"
FB_CLIENT_SECRET = "cc037fefcf9feef35a015f1767345f21"

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]

# This allows us to use a plain HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = flask.Flask(__name__)

@app.route("/db")
def db():
    conn = sqlite3.connect("users.db")
    return "Database opened successfully"
    
@app.route("/register", methods=["POSt"])
def register_account():
    name =  request.form.get('name')
    email =  request.form.get('email')
    password =  request.form.get('password')
    user_id =0
    try :
         with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO oauth_users (name,email,password)  VALUES (?,?,?)",(name,email,password) )
            user_id = cur.lastrowid
            con.commit()
            msg = "Record successfully added"
    except:
         con.rollback()
         msg = "error in insert operation"
         return msg
      
    finally:
         
         con.close()
    return "register successfully" 
    
 
    
@app.route("/login", methods=["POSt"])
def user_login():
   
    email =  request.form.get('email')
    password =  request.form.get('password')

    try :
         with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            cur.execute("select * from oauth_users  where email = '"+str(email)+"' ans password='"+str(password)+"'"  )
            rows = cur.fetchall()
            return jsonify(rows)
            if len(rows) > 0 :
                return jsonify(rows[0])
            
            return "no data"
            
            
    except:
         con.rollback()
         msg = "error in login operation"
         return msg
      
    finally:
         
         con.close()
    return "not login"
    
 
@app.route("/")
def index():
    return """
    <a href="/fb-login">Login with Facebook</a>
    """


@app.route("/fb-login")
def login():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri=URL + "/people/auth/facebook/callback", scope=FB_SCOPE
    )
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/people/auth/facebook/callback")
def callback():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/people/auth/facebook/callback"
    )

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response=flask.request.url,
    )

    # Fetch a protected resource, i.e. user profile, via Graph API

    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,posts{place},picture{url}"
    ).json()
    places = []
    user_id = facebook_user_data["id"]
    email = facebook_user_data["email"]
    name = facebook_user_data["name"]
    posts = facebook_user_data["posts"]["data"]
    

    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")
    user_id =0
    try :
         with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            # = (Int64)Command.ExecuteScalar();
            cur.execute("INSERT INTO oauth_users (name,email,password)  VALUES (?,?,?)",(name,email,"123456") )
            user_id = cur.lastrowid
            con.commit()

            msg = "Record successfully added"
    except:
         con.rollback()
         msg = "error in insert operation user"
         return msg
      
    finally:
         
         con.close()
    for place in posts :
        if place.__contains__("place") :
            try :
                with sqlite3.connect("users.db") as con:
                    cur = con.cursor()
                    # = (Int64)Command.ExecuteScalar();
                    cur.execute("INSERT INTO user_places (place_id,name,lat,lng, user_id ) VALUES (?,?,?,?,?)",(place["place"]["id"],place["place"]["name"],place["place"]["latitude"],place["place"]["longitude"] , user_id) )
                    
                    con.commit()

                    msg = "Record successfully added"
            except:
                con.rollback()
                msg = "error in insert operation place"
                return msg
            places.append(place) 

    return f"""
    User information: <br>
    User ID: {user_id} <br>
    Name: {name} <br>
    Email: {email} <br>
    Places: {len(places)} <br>
    Places array: {str(places)} <br>
    Avatar <img src="{picture_url}"> <br>
    <a href="/">Home</a>
    """


if __name__ == "__main__":
    app.run(debug=True)