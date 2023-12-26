from flask import Flask, jsonify, render_template, request, redirect, url_for
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
import random
import os


app = Flask(__name__)


# Creating database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Creating database tabel
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


class AddCafes(FlaskForm):
    name = StringField(label="Enter The Name of The Cafe", validators=[DataRequired()])
    map_url = StringField(label="Enter Cafe's Map URL", validators=[DataRequired()])
    img_url = StringField(label="Enter Cafe's Image URL", validators=[DataRequired()])
    location = StringField(label="Enter Cafe's Location", validators=[DataRequired()])
    has_sockets = SelectField(label="Does The Cafe Have Sockets?", choices=["True", "False"]
                              , validators=[DataRequired()])
    has_toilet = SelectField(label="Does The Cafe Have Toilets?", choices=["True", "False"]
                             , validators=[DataRequired()])
    has_wifi = SelectField(label="Does The Cafe Have Wifi?", choices=["True", "False"]
                           , validators=[DataRequired()])
    can_take_calls = SelectField(label="Are Phone Calls Allowed?", choices=["True", "False"]
                                 , validators=[DataRequired()])
    seats = SelectField(label="Does The Cafe Have Seats?",
                        choices=["0 - 10", "10 - 20", "20 - 30", "30 - 40", "40 - 50", "50+"],
                        validators=[DataRequired()])
    coffee_price = StringField(label="Enter The Price of The Coffee",  validators=[DataRequired()])
    submit = SubmitField("Add Cafe")


app.config['SECRET_KEY'] = os.environ.get("APP_CONFIG_SECRET")
Bootstrap5(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cities")
def cities():
    return render_template("cafes.html")


@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/cafes")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return render_template("cafes.html", cafes=all_cafes)


@app.route("/<location>", methods=["GET", "POST"])
def get_cafe_at_location(location):
    query_location = request.form.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    return render_template("location.html", cafes=all_cafes)


@app.route("/suggest_cafe", methods=["GET", "POST"])
def suggest_cafe():
    form = AddCafes()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=bool(form.has_sockets.data),
            has_toilet=bool(form.has_toilet.data),
            has_wifi=bool(form.has_wifi.data),
            can_take_calls=bool(form.can_take_calls.data),
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template("suggest_cafe.html", form=form)


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/delete_cafe")
def delete_cafe():
    cafe_id = request.args.get('id')
    cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('delete_success'))


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/delete_success")
def delete_success():
    return render_template("delete_cafe.html")


if __name__ == '__main__':
    app.run(debug=True)

