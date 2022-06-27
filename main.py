import os

import linux
import flask
import secrets

app = flask.Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True


@app.route('/', methods=['GET', 'POST'])
def login():
    if flask.request.form.get('logout'):
        flask.session['user'] = None
        return flask.redirect('/')

    if user := flask.session.get('auth_user'):
        return flask.redirect(f'/linux/home/{user}')

    if flask.request.method != 'POST':
        return flask.render_template('login.html')

    user, password = flask.request.form.get('username'), flask.request.form.get('password')

    if linux.auth(user, password):
        flask.session['user'] = user
        return flask.redirect(f'/linux/home/{user}')

    flask.flash('Nom de compte ou mot de passe invalide !')
    return flask.redirect('/')


@app.route('/linux/', defaults={'root': ''})
@app.route('/linux/<path:root>', methods=['GET'])
def get(root: str):
    user = flask.session.get('user')

    if user is None:
        flask.flash("Vous n'êtes pas connecté !")
        return flask.redirect('/')

    if not os.path.exists(f'/{root}'):
        flask.flash("Ce dossier ou fichier n'existe pas !")
        return flask.redirect(f'/linux/home/{user}')

    if not root.startswith(f'home/{user}'):
        flask.flash("Vous n'avez pas la permission d'accéder aux fichiers des autres")
        return flask.redirect(f'/linux/home/{user}')

    path, parent = linux.parse_path(root)
    file_name, file_content = '', None

    if os.path.isfile(f'/{root}'):
        try:
            with open(f'/{root}') as file:
                path = parent
                file_name = file.name.split('/')[-1]
                file_content = file.read()
        except Exception:
            flask.flash("Le fichier ne peut pas être lu !")
            flask.redirect(parent)

    return flask.render_template(
        'index.html', content=linux.get_files(path), parent=parent,
        cwd=root, file_name=file_name, file_content=file_content, history=None
    )


@app.route('/linux/', defaults={'root': ''})
@app.route('/linux/<path:root>', methods=['POST'])
def post(root: str):
    if flask.request.form.get('logout'):
        flask.session['is_root'] = None
        flask.session['user'] = None
        return flask.redirect('/')

    return flask.redirect(root)
