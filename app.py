from datetime import datetime
import json 
import os
from flask import Flask
from flask import render_template,request, redirect, session
import requests
from flaskext.mysql import MySQL
from flask import send_from_directory 

app=Flask(__name__)
app.secret_key="develoteca"
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)


 

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)

@app.route('/libros')
def libros():
    ruta = 'templates/sitio/json/json.json'  
    #print(valores)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros` WHERE fecha = CURRENT_DATE ")
    libros=cursor.fetchall()
    conexion.commit() 
    return render_template('sitio/libros.html',libros=libros)

@app.route('/libros/<name>')
def librosdetalle(name=None):
     
    sql="SELECT * FROM `libros` WHERE fecha = CURRENT_DATE  and id = %s "
    datos=(name)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    libros=cursor.fetchall()
    
    conexion.commit() 
    return render_template('/sitio/detalles.html',libros=libros)

@app.route('/pokemon')
def pokemon():
     
    datosOb=requests.get('https://pokeapi.co/api/v2/pokemon?limit=20')
    datosJson=datosOb.json() 
     
    return render_template('/sitio/pokemon.html',pokemon=datosJson['results'])

@app.route('/pokemon/<id>')
def pokemonDetalle(id=None):
     
    datosOb=requests.get('https://pokeapi.co/api/v2/pokemon/'+id)
    datosJson=datosOb.json() 
    print(datosJson['abilities'])
    return render_template('/sitio/pokemonDetalle.html',pokemon= datosJson['abilities']) 

@app.route('/superpoderosas')
def superpoderosas():
    with open('templates/sitio/json/json.json'  ,encoding="utf8") as contenido:
        valores=json.load(contenido) 

    return render_template('sitio/superpoderosas.html',valores=valores)


@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/nosotros')
def nosotrosadmin():
    return render_template('admin/nosotros.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect("/admin/login")
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    if 'login' in session:
        return redirect("/admin/")
    return render_template('admin/login.html')

@app.route('/admin/login',methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    sql="SELECT nombre FROM `usuarios` WHERE user = %s and password = %s;"
    datos=(_usuario,_password)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    dt=cursor.fetchall()
    dts=cursor.rowcount
    conexion.commit()
    if dts>0:
        session["login"]=True
        #nombre del usuario puede remplazar el texto "administrador"
        session["usuario"]=dt[0][0]
        return redirect("/admin")
    return render_template('admin/login.html',mensaje="Acceso denegado")

@app.route('/admin/cerrar')
def admin_cerrar():
    session.clear()
    return redirect('/admin/login')
    
@app.route('/admin/libros')
def admin_libros():
    if not 'login' in session:
        return redirect("/admin/login")
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)
    return render_template('admin/libros.html',libros=libros)
    
@app.route('/admin/libros/guardar',methods=['POST'])
def admin_libros_guardar():
    if not 'login' in session:
        return redirect("/admin/login")

    _nombre=request.form['txtnombre']
    _url=request.form['txturl']
    _contenido=request.form['txtcontenido']
    _archivo=request.files['txtimagen']
    _fecha= request.form['txtfecha']
    
    tiempo= datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')
    

    if _archivo.filename !="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)
    #INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`, `contenido`) VALUES (NULL, 'probando', 'imagen', 'www.html.html', '<strong>Probando Texto HTML</strong>');
    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`,`contenido`,`fecha`) VALUES (NULL, %s, %s, %s,%s,%s);"
    datos=(_nombre,nuevoNombre,_url,_contenido,_fecha)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()
    print(_nombre)
    print(_url)
    print(_archivo)
    
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar',methods=['POST'])
def admin_libros_borrar():
    if not 'login' in session:
        return redirect("/admin/login")

    _id=request.form['txtid']
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM libros WHERE `id` = %s",(_id))
    lib=cursor.fetchall()
    conexion.commit()
    
##eliminando imagenes de la carpeta
    if os.path.exists("templates/sitio/img/"+str(lib[0][0])):
        os.unlink("templates/sitio/img/"+str(lib[0][0]))

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE  `id` = %s",(_id))
    conexion.commit()
     
    
    return redirect('/admin/libros')


if __name__ == '__main__':
    app.run(debug=True)
 