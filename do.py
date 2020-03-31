#!/usr/bin/python
# -*- coding: latin-1 -*-

#!/usr/bin/python3

import pymysql
import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def to_title(snake_str):
    components = snake_str.split('_')
    return ' '.join(x.title() for x in components)


host = "HOST"
user = "USER"
password = "PASSWORD"
database = "DATABASE"
db = pymysql.connect(host, user, password, database)
cursor = db.cursor()

cursor.execute("SHOW tables")
data = cursor.fetchall()

f = open("plantilla/web.p_php", "r")
Web_org_php = f.read()
f.close()
Web_all = ""

#Crea directorios de salida
if not os.path.exists("salida"):
    os.makedirs("salida")
if not os.path.exists("salida/Modelos"):
    os.makedirs("salida/Modelos/")
if not os.path.exists("salida/Controlador"):
    os.makedirs("salida/Controlador")
if not os.path.exists("salida/React"):
    os.makedirs("salida/React")

for tablas in data:
    Modelo_php = ''
    tabla = tablas[0]
    cursor.execute("SHOW columns FROM " + tabla + ";")
    campos = cursor.fetchall()

    datos = cursor.fetchall()
    cursor.execute("SELECT table_comment FROM INFORMATION_SCHEMA.TABLES WHERE table_schema='" + database + "' AND table_name='" + tabla + "';")
    json_comment = cursor.fetchone()[0]
    parsed_json = (json.loads(json_comment))
    plural = parsed_json["plural"]
    Plural = plural.capitalize()
    singular = parsed_json["singular"]
    Singular = singular.capitalize()

    lista_campos = ''
    lista_campos_controlador = ''
    lista_campos_estado = "      id: \"\",\n"
    lista_campos_estado_row = "      id: row.id,\n"
    lista_campos_estado_nuevo = "      id: \"\",\n"
    lista_campo_data = ""
    lista_campo_id_data = "      id: this.state.id,\n"
    lista_on_change = ""
    lista_campo_tabla = ""
    lista_inputs = ""
    coma = 0
    for campo in campos:
        if campo[0] != 'id':
            if coma >= 1:
                lista_campos += ", "
                lista_campos_estado_row += ",\n"
                lista_campos_estado_nuevo += ",\n"
                lista_campo_data += ",\n"
                lista_campo_id_data += ",\n"
            lista_campos += "'" + campo[0] + "'"
            lista_campos_controlador += "            $" + singular + "->" + campo[0] + " = $request->" + campo[0] + ";\n"
            lista_campos_estado += "      " + campo[0] + ": \"\",\n"
            lista_campos_estado_row += "      " + campo[0] + ": row." + campo[0]
            lista_campos_estado_nuevo += "      " + campo[0] + ": \"\""
            lista_campo_data += "      " + campo[0] + ": this.state." + campo[0]
            lista_campo_id_data += "      " + campo[0] + ": this.state." + campo[0]
            campo_camel = to_camel_case(campo[0])
            campo_titulo = to_title(campo[0])
            lista_on_change += "  onChange" + campo_camel + " = e => {\n"
            lista_on_change += "    this.setState({ " + campo[0] + ": e.target.value });\n"
            lista_on_change += "  };\n\n"
            lista_campo_tabla += "      {\n"
            lista_campo_tabla += "        dataField: \"" + campo[0] + "\",\n"
            lista_campo_tabla += "        text: \"" + campo_titulo + "\",\n"
            lista_campo_tabla += "        sort: true\n"
            lista_campo_tabla += "      },\n"
            lista_inputs += "            " + campo_titulo + ":\n"
            lista_inputs += "            <input\n"
            lista_inputs += "              className=\"form-control\"\n"
            lista_inputs += "              type=\"text\"\n"
            lista_inputs += "              name=\"" + campo[0] + "\"\n"
            lista_inputs += "              value={this.state." + campo[0] + "}\n"
            lista_inputs += "              onChange={this.onChange" + campo_camel + "}\n"
            lista_inputs += "            />\n"
            coma += 1
    cursor.execute("SHOW KEYS FROM " + tabla + " WHERE Key_name = 'PRIMARY';")
    llave_primaria = cursor.fetchall()[0][4]

    #Modelo
    f = open("plantilla/Model.p_php", "r")
    Modelo_php = f.read()
    f.close()
    Modelo_php = Modelo_php.replace("tabla", tabla)
    Modelo_php = Modelo_php.replace("Singular", Singular)
    Modelo_php = Modelo_php.replace("lista_campos", lista_campos)
    text_file = open("salida/Modelos/" + Singular + ".php", "w")
    text_file.write(Modelo_php)
    text_file.close()
    print("salida/Modelos/" + Singular + ".php")

    #Controlador
    f = open("plantilla/Controlador.p_php", "r")
    Controlador_php = f.read()
    f.close()
    Controlador_php = Controlador_php.replace("Singular", Singular)
    Controlador_php = Controlador_php.replace("singular", singular)
    Controlador_php = Controlador_php.replace("lista_campos_controlador", lista_campos_controlador)
    text_file = open("salida/Controlador/" + Singular + "Controller.php", "w")
    text_file.write(Controlador_php)
    text_file.close()
    print("salida/Controlador/" + Singular + "Controller.php")

    #React
    f = open("plantilla/React.p_js", "r")
    React_js = f.read()
    f.close()
    React_js = React_js.replace("Singular", Singular)
    React_js = React_js.replace("singular", singular)
    React_js = React_js.replace("Plural", Plural)
    React_js = React_js.replace("plural", plural)
    React_js = React_js.replace("lista_campos_estado_row", lista_campos_estado_row)
    React_js = React_js.replace("lista_campos_estado_nuevo", lista_campos_estado_nuevo)
    React_js = React_js.replace("lista_campo_data", lista_campo_data)
    React_js = React_js.replace("lista_campo_tabla", lista_campo_tabla)
    React_js = React_js.replace("lista_on_change", lista_on_change)
    React_js = React_js.replace("lista_inputs", lista_inputs)
    React_js = React_js.replace("lista_campos_estado", lista_campos_estado)
    React_js = React_js.replace("lista_campo_id_data", lista_campo_id_data)
    text_file = open("salida/React/" + Plural + ".js", "w")
    text_file.write(React_js)
    text_file.close()
    print("salida/React/" + Plural + ".js")

    #Web
    Web_php = Web_org_php
    Web_php = Web_php.replace("Singular", Singular)
    Web_php = Web_php.replace("plural", plural)
    Web_all += Web_php + "\n\n"

f = open("plantilla/web_done.p_php", "r")
Web_done = f.read()
f.close()
Web_done = Web_done.replace("lista_rutas", Web_all)

text_file = open("salida/web.php", "w")
text_file.write(Web_done)
text_file.close()

print("salida/web.php")
db.close()