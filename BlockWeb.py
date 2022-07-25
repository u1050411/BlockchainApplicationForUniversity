from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def inici():  # put application's code here
    return render_template('home.html')


@app.route('/professor')
def professor():  # put application's code here
    return render_template('professor.html')

@app.route('/enviar_examen')
def enviar_examen():  # put application's code here
    return render_template('enviar_examen.html')


@app.route('/alumne')
def alumne():  # put application's code here
    return render_template('estudiants.html')


if __name__ == '__main__':
    app.run(debug=True)
