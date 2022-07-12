from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def inici():  # put application's code here
    return render_template('home.html')


@app.route('/professor')
def professor():  # put application's code here
    return render_template('professor.html')


@app.route('/alumne')
def alumne():  # put application's code here
    return 'Hola Alumne'


if __name__ == '__main__':
    app.run(debug=True)
