from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://Prueba:prueba@cluster0.xv7cj.mongodb.net/flask?retryWrites=true&w=majority'
mongo = PyMongo(app)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'bdb20eaa9eef3c'
app.config['MYSQL_DATABASE_PASSWORD'] ='d0387f2a'
app.config['MYSQL_DATABASE_DB'] = 'heroku_42078ca09a517b2'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-east-02.cleardb.com'
mysql.init_app(app)


@app.route('/')
def bienvenidos():
    return render_template("bienvenidos.html")
    
@app.route('/login', methods = ['POST','GET'])
def login():
    username=""
    password=""
    error1=""
    error2=""
    erorAuth=""
    if request.method ==  "POST":
        username = request.form['username']
        password = request.form['password']
        if len(username)>12:
            error1="maximo se permite 12 caracteres para el usuario"
        if len(password)!=7:
            error2= "clave invalida"
        erorAuth = auth_login(username,password)
        if error1=="" and error2=="" and erorAuth == "":
            return render_template("index.html")
    else:
        mensaje = "Auth: "+ erorAuth + " error en campos: " +error1 + ", "+error2
        return render_template("login.html", error = mensaje )

@app.route('/registro', methods = ['POST','GET'])
def registro():
    #Variables a validar
    nombre=""
    usuario=""
    clave=""
    confirmacion=""
    #
    error1=""
    error2=""
    error3=""
    error4=""
    print("inicio")
    if request.method ==  "POST":
    #validar
        nombre = request.form['nombre']
        correo = request.form['correo']
        usuario = request.form['usuario']
        clave = request.form['clave']
        confirmacion = request.form['confirmacion']
        #condiciones de validación de datos 
        if len(nombre.split(" "))>3:
            error1= "digite su nombre corecto"
        if len(usuario)>12:
            error3="maximo se permite 12 caracteres para el usuario"
        if len(clave)!=7:
            error2= "clave invalida"
        if (clave!=confirmacion):
            error4= "no conside con la clave"
        print (error1+error2+error3+error4)
        # Validacion e insersion
        newUser = insert_new_user(nombre,correo,usuario,clave)
        #Validación correcta
        if error1=="" and error2=="" and error3==""and error4=="" and newUser == "":
            print("si entra")
            # print("usuario insertado:" + newUser.get('nombre'))
            return render_template("index.html")            
        else:
            return render_template("registro.html",error1=error1,error2=error2,error3=error3,error4=error4,errorRegist=newUser)
    print("fin")
    return render_template("registro.html")
# @app.route('/index',methods = ['POST','GET'])
@app.route('/index')
def index():
    print("si entra a index")
    return render_template("index.html")
@app.route('/peso')
# @app.route('/index',methods = ['POST','GET'])
def peso():
    return render_template("peso.html")
@app.route('/sensor')
# @app.route('/index',methods = ['POST','GET'])
def sensor():
    read = readTables("sensorFreeStyle")
    return render_template("sensor.html", read = read )
@app.route('/graficainsulina')
# @app.route('/index',methods = ['POST','GET'])
def graficainsulina():
    read = readLastData("sensorFreeStyle","dateString")
    # print(read)
    (date,valGlucosa) = ordenarGrafica(read, 1 , 5 )
    return render_template("graficainsulina.html",dateGlucosa = date, glucosa = valGlucosa)
@app.route('/graficapeso')
# @app.route('/index',methods = ['POST','GET'])
def graficapeso():
    read = readLastData("pesousuarios","fecha")
    (date,valPeso) = ordenarGrafica( read, 2, 1)
    print(date)
    return render_template("graficapeso.html",datePeso = date, peso = valPeso)
@app.route('/graficacircular')
def graficacircular():
    read = readTables("sensorFreeStyle")
    zonasGraficaC = datacircular(read,5, 80, 120)
    print(type(zonasGraficaC))
    return render_template("graficacircular.html",zonasGraficaC = zonasGraficaC)
@app.route('/graficacircularpeso')
def graficacircularpeso():
    read = readTables("pesousuarios")
    zonasGraficaC = datacircular(read,1,60,80)
    return render_template("graficacircularpeso.html",zonasGraficaC = zonasGraficaC)
def insert_new_user(name,email,user,password):
    newUser = {
        'nombre': name,
        'correo': email,
        'user': user,
        'password': password,
    }
    error_duplicate_user = auth_register(user)
    if error_duplicate_user == "":
        doc = mongo.db.users.insert(newUser)
        return error_duplicate_user
    else:
        return error_duplicate_user
def auth_login(userName,password):
    authenticate = mongo.db.users.find_one({'user':userName})
    error = ""

    print(authenticate.get('user')+authenticate.get('password'))
    if authenticate.get('user') != userName and (authenticate.get('password') != password):
        error = "Ha ocurrido un erro al digitar el usuario o contraseña"
    return error
def auth_register(userName):
    authenticate = mongo.db.users.find_one({'user':userName})
    error = ""
    print(type(authenticate))
    print(authenticate.get('user')+authenticate.get('password'))
    if authenticate.get('user') == userName :
        error = "Usuario ya existente"
    return error
def coutData():
    db2 =  mysql.connect()
    mycursor = db2.cursor()
    querry = "select count(*) from sensorFreeStyle"
    error = ""
    try:
        mycursor.execute(querry)
        countData = mycursor.fetchone()
        print(countData[0])
        print("count row :", mycursor.rowcount)
        db2.commit()
        db2.close()
        return countData[0]
    except:
        print("Eror: "+ error)
        db2.close()
        countData = "vacio"
        return countData
    print(" ")
def readTables(tabla):
    db2 =  mysql.connect()
    mycursor = db2.cursor()
    querry = "select * from " + tabla
    error = ""
    try:
        mycursor.execute(querry)
        readData = mycursor.fetchall()
        print(readData)
        print("count row :", mycursor.rowcount)
        db2.commit()
        db2.close()
        return readData
    except:
        print("Eror: "+ error)
        db2.close()
        readData = "vacio"
        return readData
def datacircular(tuplaMySQL, indice, bajaNormal, normalAlta):
    zonasDataUser =[0,0,0]
    for valData in tuplaMySQL:
        if valData[indice] >= bajaNormal and valData[indice] <= normalAlta :
            zonasDataUser[1] += 1#   Zona media (Nivel sanoooo)
        elif valData[indice] > normalAlta:
            zonasDataUser[2] += 1#   Zona Alta (Hiperglucemico)
        elif valData[indice] < bajaNormal:
            zonasDataUser[0] += 1#   Zona Baja (Hipoglucemico)
        # print("0-"+ str(zonasDataUser[0]) + " 1-"+ str(zonasDataUser[1]) + " 2-"+ str(zonasDataUser[2]))
    return zonasDataUser
def readLastData(tabla,campo):
    db2 =  mysql.connect()
    mycursor = db2.cursor()
    lecturaDesc = "order by "+ campo +" desc limit 7"
    querry = "select * from " + tabla +" "+ lecturaDesc
    error = ""
    try:
        mycursor.execute(querry)
        readData = mycursor.fetchall()
        print(readData)
        print("count row :", mycursor.rowcount)
        db2.commit()
        db2.close()
        return readData
    except:
        print("Eror: "+ error)
        db2.close()
        readData = "vacio"
        return readData
#   Return (Date, Val peso)
def ordenarGrafica(tuplaMySQL,indDate,indVal):
    dataVal     = []
    dataDate    = []
    print(tuplaMySQL)
    for dataTable in tuplaMySQL:
        dataDate.append(str(dataTable[indDate]))
        dataVal.append(int(dataTable[indVal]))
    return (dataDate, dataVal)

if __name__ == "__main__":
    app.run(debug=1)


    # return render_template('index.html')
    # Terminal de visual
    # 1. Crear un entorno virtual en la carpeta: py -3 -m venv env (solo una vez por proyecto)
    # 2. Entrar a la carpeta entorno virtual: env\Scripts\activate.bat
 
