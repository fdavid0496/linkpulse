"""
LinkPulse - Backend (Flask)
Parte de Persona 2: rutas principales del acortador.

Responsabilidades de esta parte (segun division del proyecto):
1. Ruta que recibe el link largo y genera un codigo corto.
2. Ruta que redirige del codigo corto al link original.
3. Generador de codigo aleatorio de 6 caracteres.

Nota para el equipo: el almacenamiento es un diccionario en memoria (URLS_DB)
para poder probar las rutas ya mismo. Persona 3 debe reemplazar las funciones
guardar_url() y obtener_url() por las llamadas equivalentes a MongoDB,
manteniendo la misma firma (mismos parametros y mismo tipo de retorno) para
que las rutas de abajo no tengan que cambiar.
"""

import random
import string

from flask import Flask, jsonify, redirect, request

app = Flask(__name__)

# --- "Base de datos" temporal en memoria ---
# Estructura: { "codigo": {"url_original": str, "clicks": int} }
# Persona 3: reemplazar esto por la coleccion de MongoDB.
URLS_DB = {}


def generar_codigo(longitud: int = 6) -> str:
    """Genera un codigo aleatorio alfanumerico (letras + numeros).

    Se valida que no choque con uno ya existente en URLS_DB para
    evitar que dos links distintos terminen con el mismo codigo corto.
    """
    caracteres = string.ascii_letters + string.digits
    while True:
        codigo = "".join(random.choices(caracteres, k=longitud))
        if codigo not in URLS_DB:
            return codigo


def guardar_url(codigo: str, url_original: str) -> None:
    """Guarda la relacion codigo -> url original.

    Persona 3: esta funcion es el punto de reemplazo por un
    db.collection.insert_one({...}) de MongoDB.
    """
    URLS_DB[codigo] = {"url_original": url_original, "clicks": 0}


def obtener_url(codigo: str):
    """Devuelve el registro guardado para un codigo, o None si no existe.

    Persona 3: reemplazar por un db.collection.find_one({"codigo": codigo}).
    """
    return URLS_DB.get(codigo)


@app.route("/api/acortar", methods=["POST"])
def acortar_link():
    """Recibe el link largo (JSON: {"url": "..."}) y devuelve el codigo corto."""
    datos = request.get_json(silent=True) or {}
    url_original = datos.get("url")

    if not url_original:
        return jsonify({"error": "Falta el campo 'url' en el body"}), 400

    codigo = generar_codigo()
    guardar_url(codigo, url_original)

    link_corto = request.host_url + codigo

    return jsonify({
        "codigo": codigo,
        "url_original": url_original,
        "link_corto": link_corto,
    }), 201


@app.route("/<codigo>", methods=["GET"])
def redirigir(codigo):
    """Redirige al link original a partir del codigo corto."""
    registro = obtener_url(codigo)

    if registro is None:
        return jsonify({"error": "Codigo no encontrado"}), 404

    # Persona 3: aqui va el update_one para incrementar clicks en MongoDB.
    registro["clicks"] += 1

    return redirect(registro["url_original"])


@app.route("/api/stats/<codigo>", methods=["GET"])
def stats(codigo):
    """Endpoint de apoyo (no forma parte del alcance original de Persona 2).

    Solo para pruebas propias mientras se desarrolla: permite consultar el
    numero de clics de un codigo sin depender del front de Persona 3.
    """
    registro = obtener_url(codigo)

    if registro is None:
        return jsonify({"error": "Codigo no encontrado"}), 404

    return jsonify({
        "codigo": codigo,
        "url_original": registro["url_original"],
        "clicks": registro["clicks"],
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
