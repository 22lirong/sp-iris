from flask import Flask, jsonify, request, g, render_template, abort, make_response, redirect, url_for

from model.User import User
from model.Pred import Pred

from validation.Validator import *

import numpy as np
import joblib
import re

from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# landing page
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html")


# register page
@app.route("/register")
def register():
    return render_template("register.html")


# register form
@app.route('/registerUser', methods=['GET', 'POST'])
def registerUser():
    try:
        user_name = request.form['user_name']
        email = request.form['email']
        pwd = request.form['pwd']
        pwd2 = request.form['pwd2']

        print(user_name)
        print(email)
        print(pwd)
        print(pwd2)

        msg = ""

        if pwd != pwd2:
            msg = "Password and Confirm Password do not match!"
            return render_template("register.html", message = msg)

        elif not re.match(r'[A-Za-z0-9]+', user_name):
            msg = "User Name must contain only characters and numbers!"
            return render_template("register.html", message = msg)

        else:
            userJson = {
                            "user_name": user_name,
                            "email": email,
                            "password": pwd,
                            "role": "user"
                        }
            print(userJson)

            output = User.insertUser(userJson)

            return render_template("register.html", message = "You have successfully registered!")

    except Exception as err:
        print(err)
        return render_template("register.html", message = "Account already exists!")


# login page
@app.route("/login")
def login():
    return render_template("login.html")


# login form
@app.route('/loginUser', methods=['POST'])
def loginUser():
    try:
        email = request.form['email']
        pwd = request.form['pwd']

        print(email)
        print(pwd)

        output = User.loginUser({"email": email, "password":pwd})
        print(output)

        jsonUser = User.getUserId(email)
        user_id = jsonUser[0]['user_id']
        user_name = jsonUser[0]['user_name']

        print(user_id)
        print(user_name)
        
        if output["jwt"] == "":
            return render_template("login.html", message = "Invalid Login Credentials!")
       
        else:
            resp = make_response(render_template("viewPreds.html", user_id = user_id, user_name = user_name))
            resp.set_cookie('jwt', output["jwt"])
    
            return resp
    except Exception as err:
        print(err)
        return render_template("login.html",message="Error!")


# prediction page
@app.route('/viewPreds.html')
@login_required
def searchPred():
    try:
        user_id=request.args.get("user_id")
        user_name = request.args.get("user_name")

        print(user_id)
        print(user_name)
        
        jsonPreds = Pred.getPredByUser(user_id)
        #print(jsonPreds)

        return render_template("viewPreds.html", preds = jsonPreds, user_id = user_id, user_name = user_name)
    
    except Exception as err:
        print(err)
        return render_template("viewPreds.html", user_id = user_id, user_name = user_name)


# predict form
@app.route('/predict', methods = ['GET', 'POST'])
@login_required
def predict():
    try:
        sepal_length = request.form['sepal_length']
        sepal_width = request.form['sepal_width']
        petal_length = request.form['petal_length']
        petal_width = request.form['petal_width']
        user_id = request.form['user_id']
        user_name = request.form['user_name']
        
        print(sepal_length, sepal_width, petal_length, petal_width, user_id)

        # keep all inputs in array
        test_data = [sepal_length, sepal_width, petal_length, petal_width]
        print(test_data)
    
        # convert value data into numpy array
        test_data = np.array(test_data)
    
        # reshape array
        test_data = test_data.reshape(1,-1)
        print(test_data)
    
        # open file
        file = open("randomforest_model.pkl","rb")
    
        # load trained model
        trained_model = joblib.load(file)
    
        # predict
        prediction = trained_model.predict(test_data)
    
        print(prediction[0])
        
        # save data to sql
        jsonPreds = Pred.insertPred(user_id, sepal_length, sepal_width, petal_length, petal_width, prediction[0])
        print(jsonPreds)
        
        return render_template("viewPreds.html", prediction = prediction,
                                                 preds = jsonPreds,
                                                 sepal_length = sepal_length,
                                                 sepal_width = sepal_width,
                                                 petal_length = petal_length,
                                                 petal_width = petal_width,
                                                 user_id = user_id,
                                                 user_name = user_name)

    except Exception as err:
        print(err)
        return render_template("viewPreds.html", user_id = user_id, user_name = user_name)


# delete predict
@app.route('/deletePred', methods = ['POST'])
@login_required
def deletePred():
    try:
        user_id = request.args.get("user_id")
        user_name = request.args.get("user_name")

        print(user_id)
        print(user_name)
        
        pred_id = request.args.get("pred_id")
        print(pred_id)

        output = Pred.deletePred(pred_id)

        resp = make_response(render_template("viewPreds.html", user_id = user_id, user_name = user_name))
        return resp
        
    except Exception as err:
        print(err)
        return render_template("login.html")


# logout
@app.route('/logout')
def logout():
    resp = make_response(redirect("/"))
    resp.delete_cookie('jwt')
    
    return resp


@app.route('/<string:url>')
def staticPage(url):
    try:
        return render_template(url)
    except Exception as err:
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
