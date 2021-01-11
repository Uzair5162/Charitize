from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json
import config   #File with api credentials

app_id = config.app_id
app_key = config.app_key

parameters = {
    "app_id": app_id,
    "app_key": app_key,
    "pageSize": 10,
    "pageNum": 1,
    "search": "medical",
    "searchType": "DEFAULT"
}

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find', methods=['POST', 'GET'])
def find():
    if request.method == 'POST':
        # 'searchCharity' is the NAME of the HTML input that is used in the POST call
        searchKeyword = request.form['searchCharity']
        parameters["search"] = searchKeyword

        response = requests.get("https://api.data.charitynavigator.org/v2/Organizations", params=parameters, verify=False)

        names = []
        cities = []
        urls = []
        for charity in response.json():
            # print(charity["charityName"])
            names.append(charity["charityName"].title())
            cities.append(charity["mailingAddress"]["city"].title() + ", " + charity["mailingAddress"]["stateOrProvince"].upper())
            urls.append(charity["charityNavigatorURL"])

        return render_template('find.html', names=names, cities=cities, urls=urls)

    else:
        # tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('find.html')

@app.route('/donations')
def donations():
    return render_template('donations.html')

if __name__ == "__main__":
    app.run(debug=True)