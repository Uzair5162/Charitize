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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donations.db'
db = SQLAlchemy(app)

class Donations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, default=0)
    foundation = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Donation %r>' % self.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find', methods=['POST', 'GET'])
def find():
    if request.method == 'POST':
        # 'searchCharity' is the NAME of the HTML input that is used in the POST call
        searchKeyword = request.form['searchCharity']
        numResults = request.form['quantity']

        if not searchKeyword:
            searchKeyword = "medical"

        parameters["search"] = searchKeyword
        parameters["pageSize"] = numResults

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
        return render_template('find.html')

@app.route('/donations', methods=['POST', 'GET'])
def donations():
    if request.method == 'POST':
        dollarAmount = request.form['amountDonated']
        foundationName = request.form['foundationName']

        if not foundationName:
            foundationName = "Blank"
        
        if not bool(dollarAmount):
            dollarAmount = 0

        new_donation = Donations(amount=dollarAmount, foundation=foundationName)

        try:
            db.session.add(new_donation)
            db.session.commit()
            return redirect('/donations')
        except:
            return 'There was an issue adding your donation'

    else:
        donations = Donations.query.order_by(Donations.date_created).all()
        return render_template('donations.html', donations=donations)

@app.route('/delete/<int:id>')
def delete(id):
    donation_to_delete = Donations.query.get_or_404(id)

    try:
        db.session.delete(donation_to_delete)
        db.session.commit()
        return redirect('/donations')
    except:
        return 'There was a problem deleting that donation'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    donation_to_update = Donations.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']

        if not name:
            name = "Blank"

        if not bool(number):
            number = 0

        donation_to_update.foundation = name
        donation_to_update.amount = number
        
    else:
        return render_template('update.html', donation = donation_to_update)

    try:
        db.session.commit()
        return redirect('/donations')
    except:
        return 'There was a problem updating that Donation'

if __name__ == "__main__":
    app.run(debug=True)