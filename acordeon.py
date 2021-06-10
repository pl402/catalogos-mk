#!//usr/bin/python3
# -*- coding: latin-1 -*-

import pymysql
import json
import os

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def to_title(snake_str):
    components = snake_str.split('_')
    return ' '.join(x.title() for x in components)

def busca_formato(indet, formatos):
    global cursor, out
    out += "<ul className=\"indent-" + str(indet) +"\">\n"
    formatos = [x.strip() for x in formatos.split(',')]
    for cve_formato in formatos:
        cursor.execute("SELECT titulo FROM anexos WHERE clave = '" + cve_formato + "';")
        data = cursor.fetchall()
        for titulos_formato in data:
            titulo_form = titulos_formato[0]
            if titulo_form != 'sin titulo':
                out += "<li><b>" + cve_formato + "</b> " + titulo_form + "</li>\n"
    out += "</ul>\n"
op_dir = os.path.dirname(os.path.realpath(__file__))


out = ""

with open(op_dir + "/config.json") as f:
  config = json.load(f)
host = config["host"]
user = config["user"]
password = config["password"]
database = config["database"]
url_laravel_api = config["url_laravel_api"]

db = pymysql.connect(host, user, password, database)
cursor = db.cursor()
cursor.execute("SELECT dirgral FROM admin_er.ambitos group by dirgral ORDER BY indice;")
data = cursor.fetchall()
eventKey = 0
for direcciones_generales in data:
    nombre_dirgen = str(direcciones_generales[0])
    out += "<Card>\n"
    out += "    <Card.Header>\n"
    out += "        <Accordion.Toggle as={Button} variant=\"link\" eventKey=\"" + str(eventKey) + "\">\n"
    out += "        "+ nombre_dirgen +"\n"
    out += "        </Accordion.Toggle>\n"
    out += "    </Card.Header>\n"
    out += "    <Accordion.Collapse eventKey=\"" + str(eventKey) + "\">\n"
    out += "        <Card.Body>\n"

    cursor.execute("SELECT formatos FROM ambitos WHERE dir IS NULL AND formatos IS NOT NULL AND dirgral = '" + nombre_dirgen + "';")
    form_dirgen = cursor.fetchall()
    for formatos_print_dir_gen in form_dirgen:
        busca_formato(1, formatos_print_dir_gen[0])

    cursor.execute("SELECT dir FROM admin_er.ambitos WHERE dirgral = '" + nombre_dirgen + "' group by dir ORDER BY indice;")
    data2 = cursor.fetchall()
    for direcciones in data2:
        nombre_dir = str(direcciones[0])
        out += "<h4 className=\"indent-1\">" + nombre_dir + "</h4>\n"
        cursor.execute("SELECT formatos FROM ambitos WHERE depto IS NULL AND formatos IS NOT NULL AND dirgral = '" + nombre_dirgen + "' AND dir = '" + nombre_dir + "';")
        form_dir = cursor.fetchall()
        for formatos_print_dir in form_dir:
            busca_formato(2, formatos_print_dir[0])

        cursor.execute("SELECT depto FROM admin_er.ambitos WHERE dirgral = '" + nombre_dirgen + "' AND dir = '" + nombre_dir + "' ORDER BY indice;")
        data3 = cursor.fetchall()
        for direcciones in data3:
            depto = str(direcciones[0])
            out += "<h5 className=\"indent-2\">" + depto + "</h5>\n"
            cursor.execute("SELECT formatos FROM ambitos WHERE formatos IS NOT NULL AND dirgral = '" + nombre_dirgen + "' AND dir = '" + nombre_dir + "' AND depto = '" + depto + "';")
            form_depto = cursor.fetchall()
            for formatos_print_depto in form_depto:
                busca_formato(3, formatos_print_depto[0])

    out += "        </Card.Body>\n"
    out += "    </Accordion.Collapse>\n"
    out += "</Card>\n"
    eventKey += 1

text_file = open(op_dir + "/salida/acordeon.js", "w")
text_file.write(out)
text_file.close()