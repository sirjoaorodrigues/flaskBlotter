import pandas as pd
from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from data import PNL
import os

from forms import RegistrationForm, LoginForm
from models import User, app, db, Operacao

import sqlite3
import json

with app.app_context():
    db.create_all()

login_manager = LoginManager(app)
login_manager.login_view = 'login'
ALLOWED_EXTENSIONS = {'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('blotter'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/blotter', methods=['GET', 'POST'])
@login_required
def blotter():

    if request.method == "POST":
        ativo = request.form["ativo"]
        estrategia = request.form['estrategia']
        fundo = request.form['fundo']
        quantidade = float(request.form["quantidade"])
        preco = float(request.form["preco"])
        data = request.form["data"]

        nova_operacao = Operacao(
            ativo=ativo,
            estrategia=estrategia,
            fundo=fundo,
            quantidade=quantidade,
            preco=preco,
            data=data,
            user=current_user.username
        )

        db.session.add(nova_operacao)
        db.session.commit()

        return redirect(url_for("blotter"))
    operacoes = Operacao.query.all()
    return render_template("blotter.html", boletos=operacoes)


@app.route("/blotter/excluir/<int:id>", methods=["POST"])
@login_required
def excluir(id):
    operacao = Operacao.query.get_or_404(id)
    db.session.delete(operacao)
    db.session.commit()
    return redirect(url_for("blotter"))


@app.route("/blotter/upload", methods=["POST"])
@login_required
def upload():
    if 'file' not in request.files:
        flash("Nenhum arquivo enviado.")
        return redirect(url_for("index"))

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        flash("Arquivo inválido. Envie um .xlsx.")
        return redirect(url_for("index"))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)

    try:
        df = pd.read_excel(filepath)
        for _, row in df.iterrows():
            ativo = row['ativo']
            estrategia = row['estrategia']
            fundo = row['fundo']
            quantidade = float(row['quantidade'])
            preco = float(row['preco'])

            row['data'] = pd.to_datetime(row['data'])
            data = row['data'].strftime("%Y-%m-%d")

            operacao = Operacao(
                ativo=ativo,
                quantidade=quantidade,
                estrategia=estrategia,
                preco=preco,
                fundo=fundo,
                data=data,
                user=current_user.username
            )
            db.session.add(operacao)

        db.session.commit()
        flash("Boletas importadas com sucesso!")
    except Exception as e:
        flash(f"Erro ao processar a planilha: {str(e)}")

    return redirect(url_for("blotter"))


@app.route('/closing-pnl', methods=['GET', 'POST'])
def closing_pnl():
    pnl = PNL()
    funds = {
        'Multiestrategia': '111376',
        'Ibovespa': '189529',
        'ALOCACAO': '306274',
        'BDR': '1006215',
        'ELETROBRAS': '2200899',
        'TOP JUROS': '10553193',
        'DAYC ARBITRAGEM': '9735925',
        'IRFM1': '152196',
        'SOCJOV II': '8366977'
    }
    selected = []
    df = pd.DataFrame()
    bps = None

    if request.method == 'POST':

        selected = request.form.getlist('ids')
        df = pnl.get_pnl_closing(selected)[0]
        bps = round(pnl.get_pnl_closing(selected)[1], 2)

        if 'atualiza_preco' in request.form:
            pnl.update_prices()
            bps = round(pnl.get_pnl_closing(selected)[1], 2)
            df = pnl.get_pnl_closing(selected)[0]

    return render_template('management_panel.html',
                           ids=funds,
                           selecionados=selected,
                           table=df.to_html(classes='data', index=False, table_id="table"),
                           titles=df.columns.values,
                           bps=bps)


@app.route('/live-pnl', methods=['GET', 'POST'])
def live_pnl():
    pnl = PNL()
    funds = {
        'Multiestrategia': '111376',
        'Ibovespa': '189529',
        'ALOCACAO': '306274',
        'BDR': '1006215',
        'ELETROBRAS': '2200899',
        'TOP JUROS': '10553193',
        'DAYC ARBITRAGEM': '9735925',
        'IRFM1': '152196',
        'SOCJOV II': '8366977'
    }
    selected = []
    df = pd.DataFrame()
    bps = None

    if request.method == 'POST':

        selected = request.form.getlist('ids')
        df = pnl.get_pnl_live(selected)[0]
        bps = round(pnl.get_pnl_live(selected)[1], 2)

        if 'atualiza_preco' in request.form:
            pnl.update_prices()
            df = pnl.get_pnl_live(selected)[0]
            bps = round(pnl.get_pnl_live(selected)[1], 2)

    return render_template('management_panel.html',
                           ids=funds,
                           selecionados=selected,
                           table=df.to_html(classes='data', index=False, table_id="table"),
                           titles=df.columns.values,
                           bps=bps)


@app.route('/api/books', methods=['GET'])
def api():

    conn = sqlite3.connect('./instance/users.db')

    df = pd.read_sql("SELECT * FROM operacao", con=conn).to_dict(orient='records')

    json_str = json.dumps(df, ensure_ascii=False)
    encoded = json_str.encode('latin-1')

    return Response(encoded, content_type='application/json; charset=latin-1')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000)
