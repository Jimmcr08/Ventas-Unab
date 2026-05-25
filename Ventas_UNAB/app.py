# app.py

from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)

app.secret_key = "unab"

USUARIOS = {

    "admin@unab.edu.co": "admin123",

    "jimmy@unab.edu.co": "abcd",

    "juan@unab.edu.co": "1234",

    "samuel@unab.edu.co": "1234"
}


def cargar_productos():

    try:

        with open("productos.json", "r") as archivo:

            return json.load(archivo)

    except:

        return []


def guardar_productos(productos):

    with open("productos.json", "w") as archivo:

        json.dump(productos, archivo, indent=4)


@app.route("/", methods=["GET", "POST"])
def login():

    error = ""

    if request.method == "POST":

        correo = request.form["correo"]

        password = request.form["password"]

        if correo in USUARIOS and USUARIOS[correo] == password:

            session["user"] = correo

            return redirect("/productos")

        else:

            error = "Datos incorrectos, inténtalo nuevamente"

    return render_template("index.html", error=error)


@app.route("/productos")
def productos():

    if "user" not in session:

        return redirect("/")

    lista = cargar_productos()

    #Solo aprobados
    
    lista = [

        p for p in lista

        if p.get("aprobado") == True
    ]

    busqueda = request.args.get("buscar", "").lower()

    categoria = request.args.get("categoria", "")

    productos_filtrados = []

    for p in lista:

        coincide_busqueda = busqueda in p["nombre"].lower()

        coincide_categoria = categoria == "" or p["categoria"] == categoria

        if coincide_busqueda and coincide_categoria:

            productos_filtrados.append(p)

    return render_template(
        "productos.html",
        productos=productos_filtrados
    )


@app.route("/agregar", methods=["GET", "POST"])
def agregar():

    if "user" not in session:

        return redirect("/")

    if request.method == "POST":

        nombre = request.form["nombre"]

        precio = request.form["precio"]

        descripcion = request.form["descripcion"]

        telefono = request.form["telefono"]

        categoria = request.form["categoria"]

        imagen1 = request.files["imagen1"]

        imagen2 = request.files["imagen2"]

        imagen3 = request.files["imagen3"]

        imagen4 = request.files["imagen4"]

        imagen5 = request.files["imagen5"]

        carpeta = "static/uploads"

        if not os.path.exists(carpeta):

            os.makedirs(carpeta)

        nombre_imagen1 = ""
        nombre_imagen2 = ""
        nombre_imagen3 = ""
        nombre_imagen4 = ""
        nombre_imagen5 = ""

        # IMAGEN 1

        if imagen1.filename != "":

            nombre_imagen1 = imagen1.filename

            ruta = os.path.join(
                carpeta,
                nombre_imagen1
            )

            imagen1.save(ruta)

        # IMAGEN 2

        if imagen2.filename != "":

            nombre_imagen2 = imagen2.filename

            ruta = os.path.join(
                carpeta,
                nombre_imagen2
            )

            imagen2.save(ruta)

        # IMAGEN 3

        if imagen3.filename != "":

            nombre_imagen3 = imagen3.filename

            ruta = os.path.join(
                carpeta,
                nombre_imagen3
            )

            imagen3.save(ruta)

        # IMAGEN 4

        if imagen4.filename != "":

            nombre_imagen4 = imagen4.filename

            ruta = os.path.join(
                carpeta,
                nombre_imagen4
            )

            imagen4.save(ruta)

        # IMAGEN 5

        if imagen5.filename != "":

            nombre_imagen5 = imagen5.filename

            ruta = os.path.join(
                carpeta,
                nombre_imagen5
            )

            imagen5.save(ruta)

        productos = cargar_productos()

        nuevo_producto = {

            "nombre": nombre,

            "precio": precio,

            "descripcion": descripcion,

            "telefono": telefono,

            "categoria": categoria,

            "imagenes":[

                nombre_imagen1,
                nombre_imagen2,
                nombre_imagen3,
                nombre_imagen4,
                nombre_imagen5
            ],

            "usuario": session["user"],

            "aprobado": False
        }

        productos.append(nuevo_producto)

        guardar_productos(productos)

        return redirect("/productos")

    return render_template("agregar.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/mis_productos")
def mis_productos():

    if "user" not in session:
        return redirect("/")

    with open("productos.json", "r") as archivo:
        productos = json.load(archivo)

    productos_usuario = []

    for p in productos:

        if p["usuario"] == session["user"]:

            productos_usuario.append(p)

    return render_template(
        "mis_productos.html",
        productos=productos_usuario
    )

@app.route("/eliminar/<nombre>")
def eliminar(nombre):

    if "user" not in session:
        return redirect("/")

    with open("productos.json", "r") as archivo:
        productos = json.load(archivo)

    nuevos_productos = []

    for p in productos:

        if p["nombre"] == nombre:

            if (
                p["usuario"] == session["user"]
                or
                session["user"] == "admin@unab.edu.co"
            ):

                continue

        nuevos_productos.append(p)

    with open("productos.json", "w") as archivo:
        json.dump(nuevos_productos, archivo, indent=4)

    return redirect("/productos")

@app.route("/aprobar/<nombre>")
def aprobar(nombre):

    if session["user"] != "admin@unab.edu.co":

        return redirect("/productos")

    productos = cargar_productos()

    for p in productos:

        if p["nombre"] == nombre:

            p["aprobado"] = True

    guardar_productos(productos)

    return redirect("/admin")

@app.route("/rechazar/<nombre>")
def rechazar(nombre):

    if session["user"] != "admin@unab.edu.co":

        return redirect("/productos")

    productos = cargar_productos()

    nuevos = []

    for p in productos:

        if p["nombre"] != nombre:

            nuevos.append(p)

    guardar_productos(nuevos)

    return redirect("/admin")

@app.route("/admin")
def admin():

    if session["user"] != "admin@unab.edu.co":

        return redirect("/productos")

    productos = cargar_productos()

    pendientes = [

        p for p in productos

        if p.get("aprobado") == False
    ]

    return render_template(

        "admin.html",

        productos=pendientes
    )

@app.route("/producto/<nombre>")
def ver_producto(nombre):

    productos = cargar_productos()

    producto = None

    for p in productos:

        if p["nombre"] == nombre:

            producto = p

            break

    if producto == None:

        return redirect("/productos")

    return render_template(

        "ver_producto.html",

        producto=producto
    )


app.run(debug=True)