from flask import Blueprint, render_template, Flask
from . import my_db

main = Blueprint('main', __name__)


@main.route('/')
def inici():  # put application's code here
    name_udg = "udg dels rosals"
    return render_template("index.html", uni=name_udg)


@main.route('/profile')
def profile():
    return render_template("profile.html")


app = Flask(__name__)
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)
