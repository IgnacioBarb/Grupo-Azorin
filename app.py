from flask import request
from flask import Flask, render_template, url_for, request, redirect, flash, session, send_file
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import pandas as pd
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_login'

csrf = CSRFProtect(app)
db = MySQL(app)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return get_by_id(db, id)


class User(UserMixin):
    def __init__(self, id, username, password, tipo, accion, lugar) -> None:
        self.id = id
        self.username = username
        self.password = password
        self.tipo = tipo
        self.accion = accion
        self.lugar = lugar

    @classmethod
    def check_password(self, password, input_password):
        return password == input_password


class Registro():
    def __init__(self, nombre, hora, fecha, accion, lugar) -> None:
        self.nombre = nombre
        self.hora = hora
        self.fecha = fecha
        self.accion = accion
        self.lugar = lugar


class Obra():
    def __init__(self, id, nombre) -> None:
        self.id = id
        self.nombre = nombre


def user_login(db, name, password):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"SELECT id, username, password, tipo FROM usuarios WHERE username = '{name}'")
        result = cursor.fetchone()
        cursor.close()
        
        if result != None:
            return User(result[0], result[1], User.check_password(
                result[2], password), result[3], None, None)
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def get_by_id(db, id):
    try:
        cursor = db.connection.cursor()
        cursor.execute(
            f"SELECT id, username, tipo, accion, lugar FROM usuarios WHERE id = '{id}'")
        result = cursor.fetchone()
        if result != None:
            return User(result[0], result[1], None, result[2], result[3], result[4])
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def get_all_users(db):
    try:
        users = []
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"SELECT id, username, password,tipo FROM usuarios")
        result = cursor.fetchall()
        if result != None:
            for i in result:
                users.append(User(i[0], i[1], i[2], i[3], None, None))
            return users
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def get_all_obras(db):
    try:
        obras = []
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"SELECT id, nombre FROM lugares")
        result = cursor.fetchall()
        if result != None:
            for i in result:
                obras.append(Obra(i[0], i[1]))
            return obras
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def get_register(db, month, year):
    try:
        registros = []
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"SELECT nombre, hora, DATE_FORMAT(fecha, '%d-%m-%Y'), accion, lugar FROM acciones_usuario WHERE YEAR(fecha) = {year} AND MONTH(fecha) = {month};")
        result = cursor.fetchall()
        if result != None:
            for i in result:
                registros.append(Registro(i[0], i[1], i[2], i[3], i[4]))
            return registros
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def insert_user(db, username, password, tipo):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"INSERT INTO usuarios (username, password, tipo) VALUES ('{username}', '{password}', '{tipo}')")
        conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def insert_obra(db, nombre):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"INSERT INTO lugares (nombre) VALUES ('{nombre}')")
        conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def user_exists(db, username):
    
    cursor = db.connection.cursor()
    cursor.execute(f"SELECT id FROM usuarios WHERE username='{username}'")
    result = cursor.fetchone()
    return result is not None


def user_delete(db, id):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(f"DELETE FROM usuarios WHERE id={id}")
        conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def obra_delete(db, id):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(f"DELETE FROM lugares WHERE id='{id}'")
        conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def update_user(db, id, username, password, tipo):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"UPDATE usuarios SET username='{username}', password='{password}', tipo={tipo} WHERE id={id}")
        conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def update_obra(db, id, name):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"UPDATE lugares SET nombre='{name}' WHERE id={id}")
        conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def add_acciones(db, username, id, accion, lugar):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(
            f"INSERT INTO acciones_usuario(nombre, hora, fecha, accion, lugar) VALUES ('{username}', NOW(),NOW(), '{accion}', '{lugar}')")
        if accion == 'terminar trabajo':
            cursor.execute(
                f"UPDATE usuarios SET accion='', lugar='' WHERE id={id}")
            conn.commit()
        else:
            cursor.execute(
                f"UPDATE usuarios SET accion='{accion}', lugar='{lugar}' WHERE id={id}")
            conn.commit()
        return True
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def get_year(db):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT DISTINCT YEAR(fecha) FROM acciones_usuario;")
        result = cursor.fetchall()
        years = []
        for i in result:
            years.append(i[0])
        return years
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def get_month(db):
    try:
        
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT DISTINCT MONTH(fecha) FROM acciones_usuario;")
        result = cursor.fetchall()
        months = []
        for i in result:
            months.append(i[0])
        return months
    except Exception as ex:
        db.connection.rollback()
        raise Exception(ex)


def descarga_registro(tabla, month, year):
    registros = []

    for i in tabla:
        registros.append([i.nombre, str(i.hora), str(i.fecha), i.accion, i.lugar])
    df = pd.DataFrame(registros,
                      columns=['nombre', 'hora', 'fecha', 'accion','lugar'])
    df.to_excel(
        f'./static/registros/registro-{month}-{year}.xlsx', index=False)
    path = f'./static/registros/registro-{month}-{year}.xlsx'
    return path


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login-fallido')
def login_fallido():
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    id_user = session['_user_id']
    user = get_by_id(db, id_user)
    if user.tipo == 1:
        users = get_all_users(db)
        return render_template('dashboard_admin.html', users=users)
    elif user.tipo == 0:
        # si accion de usuario es algo ir a ese algo
        if user.accion == 'Iniciar trabajo':
            return redirect(url_for('trabajndo'))

        if user.accion == 'Iniciar descanso':
            return redirect(url_for('descansando'))

        if user.accion == 'Terminar descanso':
            return redirect(url_for('trabajndo'))

        obras = get_all_obras(db)
        return render_template('dashboard.html', obras=obras)


@app.route('/registros', methods=['POST'])
@login_required
def registros():

    date = datetime.now()
    year = date.year
    month = date.month

    years = get_year(db)
    months = get_month(db)
    registro = get_register(db, month, year)
    return render_template('registros.html', registros=registro, year=year, month=month, years=years, months=months)


@app.route('/registro-especifico', methods=['POST'])
@login_required
def registro_especifico():

    year = request.form['year']
    month = request.form['month']
    years = get_year(db)
    months = get_month(db)
    registro = get_register(db, month, year)
    return render_template('registros.html', registros=registro, year=year, month=month, years=years, months=months)


@app.route('/trabajndo')
@login_required
def trabajndo():
    return render_template('trabajando.html')


@app.route('/descansando')
@login_required
def descansando():
    return render_template('descansando.html')


@app.route('/add-user', methods=['POST'])
@login_required
def add_user():
    submit_button_value = request.form.get('submit_button')
    if submit_button_value == 'add':
        username = request.form['username']
        password = request.form['password']
        tipo = request.form.get('tipo')
        if username == "":
            flash('Es necesario que des un usuario')
            return render_template('add_user.html')
        if password == "":
            flash('Es necesario que des una contraseña')
            return render_template('add_user.html')
        if tipo == None:
            flash('Es necesario que des un tipo de usuario')
            return render_template('add_user.html')
        if user_exists(db, username):
            flash('Ese usuario ya existe')
            return render_template('add_user.html')
        insert_user(db, username, password, tipo)
        flash('Usuario añadido')
        return redirect(url_for('dashboard'))
    elif submit_button_value == 'Cancelar':
        return redirect(url_for('dashboard'))

    return render_template('add_user.html')


@app.route('/edit-user', methods=['POST'])
@login_required
def edit_user():
    id = request.form['user_id']
    username = request.form['username']
    password = request.form['password']
    tipo = request.form['tipo']
    return render_template('edit_user.html', user=User(id, username, password, int(tipo), None, None))


@app.route('/user-update', methods=['POST'])
@login_required
def user_update():
    submit_button_value = request.form.get('submit_button')
    if submit_button_value == 'edit':
        id = request.form['user_id']
        username = request.form['username']
        password = request.form['password']
        tipo = request.form['tipo']
        update_user(db, id, username, password, tipo)
        flash('Usuario editado')
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/delete-user', methods=['POST'])
@login_required
def delete_user():
    id = request.form['user_id']
    user_delete(db, id)
    flash('Usuario eliminado')
    return redirect(url_for('dashboard'))


@app.route('/login-form', methods=['POST'])
def login_form():
    name = request.form['username']
    password = request.form['password']
    logged_user = user_login(db, name, password)
    if logged_user != None:
        if logged_user.password:
            login_user(logged_user)
            return redirect(url_for('dashboard'))
        else:
            flash('la contraseña no es correcta')
            return redirect(url_for('login'))
    else:
        flash('Usuario no encontrado')
        return redirect(url_for('login'))


@app.route('/download', methods=['get'])
@login_required
def download_file():
    year = request.args.get('year')
    month = request.args.get('month')
    path = descarga_registro(get_register(db, month, year), month, year)
    return send_file(path, as_attachment=True)


@app.route('/acciones-usuario', methods=['POST'])
@login_required
def process_form():
    accion = request.form['tipo']
    id = session['_user_id']
    user = get_by_id(db, id)
    if accion == 'Iniciar trabajo':
        lugar = request.form['lugar']
        print(request.form['ubicacion'])
        add_acciones(db, user.username, id, accion, lugar)
        return redirect(url_for('trabajndo'))

    if accion == 'Terminar trabajo':
        print(request.form['ubicacion'])
        add_acciones(db, user.username, id, accion, user.lugar)
        return redirect(url_for('dashboard'))

    if accion == 'Iniciar descanso':
        print(request.form['ubicacion'])
        add_acciones(db, user.username, id, accion, user.lugar)
        return redirect(url_for('descansando'))

    if accion == 'Terminar descanso':
        print(request.form['ubicacion'])
        add_acciones(db, user.username, id, accion, user.lugar)
        return redirect(url_for('trabajndo'))


@app.route('/atras', methods=['POST'])
@login_required
def atras():
    return redirect(url_for('dashboard'))


@app.route('/obras', methods=['POST'])
@login_required
def obras():
    return redirect(url_for('obra'))


@app.route('/obra')
@login_required
def obra():
    obras = get_all_obras(db)
    return render_template('obras.html', obras=obras)


@app.route('/delete-obra', methods=['POST'])
@login_required
def delete_obra():
    id = request.form['id']
    obra_delete(db, id)
    flash('Obra eliminada')
    return redirect(url_for('obra'))


@app.route('/add-obras', methods=['POST'])
@login_required
def add_obras():
    obras = get_all_obras(db)
    nombre = request.form['nombre']
    if nombre == '':
        flash('Necesitas dar un nombre para añdir esa obra')
        return redirect(url_for('obra'))
    for i in obras:
        if nombre == i.nombre:
            flash('Esta obra ya esta registrada')
            return redirect(url_for('obra'))

    insert_obra(db, nombre)
    return redirect(url_for('obra'))


@app.route('/editar-obra', methods=['POST'])
def editar_obra():
    id = request.form['id']
    name = request.form['name']
    update_obra(db, id, name)
    return redirect(url_for('obra'))


@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('login')


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404
