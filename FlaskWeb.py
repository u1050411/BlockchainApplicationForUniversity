from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():  # put application's code here
    return '''<div id="blue_bar">
    <div id="org_logo">
        <a href="http://www.udg.edu/" title="www.udg.edu">
            <img id="logo_img" src="/themes/adas18/static/img/logo_udg_inv.png">
        </a>
    </div>
    <div id="langs"><span id="es">Español</span> | <span id="ca" class="highlight_lang">Català</span> | <span id="en">English</span></div>
</div>
<div class="form-col1 text-question">
                        <label id="label_user" for="edit-name">Usuari</label>
                    </div>
'''


@app.route('/form-example', methods=['GET', 'POST'])
def form_example():
    # handle the POST request
    if request.method == 'POST':
        language = request.form.get('language')
        framework = request.form.get('framework')
        return '''
                  <h1>The language value is: {}</h1>
                  <h1>The framework value is: {}</h1>'''.format(language, framework)

    # otherwise handle the GET request
    return '''
           <form method="POST">
               <div><label>Language: <input type="text" name="language"></label></div>
               <div><label>Framework: <input type="text" name="framework"></label></div>
               <input type="submit" value="Submit">
           </form>'''


if __name__ == '__main__':
    app.run()
