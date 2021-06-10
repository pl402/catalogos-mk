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

# CONFIG DATA

op_dir = os.path.dirname(os.path.realpath(__file__))

with open(op_dir + "/config.json") as f:
  config = json.load(f)


host = config["host"]
user = config["user"]
password = config["password"]
database = config["database"]
url_laravel_api = config["url_laravel_api"]

db = pymysql.connect(host=host, user=user, password=password, database=database)
cursor = db.cursor()
cursor.execute("SHOW tables")
data = cursor.fetchall()

f = open(op_dir + "/plantilla/web.p_php", "r")
Web_org_php = f.read()
f.close()
Web_all = ""

App_imports = ""
App_route = ""

#Crea directorios de salida
if not os.path.exists(op_dir + "/salida"):
    os.makedirs(op_dir + "/salida")
if not os.path.exists(op_dir + "/salida/Modelos"):
    os.makedirs(op_dir + "/salida/Modelos/")
if not os.path.exists(op_dir + "/salida/Controlador"):
    os.makedirs(op_dir + "/salida/Controlador")
if not os.path.exists(op_dir + "/salida/React"):
    os.makedirs(op_dir + "/salida/React")

#Solo crea seleccionados
listaTablas = ['f94']

for tablas in data: 
    Modelo_php = ''
    tabla = tablas[0]
    if tabla in listaTablas:
        cursor.execute("SHOW columns FROM " + tabla + ";")
        campos = cursor.fetchall()


        cursor.execute("SELECT * FROM anexos WHERE clave like '" + tabla.replace("f", "") + "';")
        fdata = cursor.fetchone()

        datos = cursor.fetchall()
        cursor.execute("SELECT table_comment FROM INFORMATION_SCHEMA.TABLES WHERE table_schema='" + database + "' AND table_name='" + tabla + "';")
        json_comment = cursor.fetchone()[0]
        parsed_json = (json.loads(json_comment))
        plural = parsed_json["plural"]
        Plural = plural.capitalize()
        singular = parsed_json["singular"]
        Singular = singular.capitalize()

        Titulo_Formulario = "Catálogo de" + Plural
        Nombre_Forumulario = ""
        Num_Formato = Plural[1:-1]
        json_tooltips = False
        if fdata:
            Titulo_Formulario = fdata[2]
            Nombre_Forumulario = fdata[2].lower()
            if fdata[4]:
                json_tooltips = (json.loads(fdata[4]))
            
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
        lista_visualizar = ""
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
                if campo[0] == "ambito_id":
                    lista_campo_data += "      " + campo[0] + ": this.props.match.params.ambito_id"
                    lista_campo_id_data += "      " + campo[0] + ": this.props.match.params.ambito_id" 
                elif campo[0] == "usuario_id":
                    lista_campo_data += "      " + campo[0] + ": localStorage.id"
                    lista_campo_id_data += "      " + campo[0] + ": localStorage.id"
                else:
                    lista_campo_data += "      " + campo[0] + ": this.state." + campo[0]
                    lista_campo_id_data += "      " + campo[0] + ": this.state." + campo[0]

                campo_camel = to_camel_case(campo[0])
                campo_titulo = to_title(campo[0])
                lista_on_change += "  onChange" + campo_camel + " = e => {\n"
                lista_on_change += "    this.setState({ " + campo[0] + ": e.target.value });\n"
                lista_on_change += "  };\n\n"

                if campo[0] != "usuario_id" and campo[0] != "ambito_id":
                    lista_campo_tabla += "      {\n"
                    lista_campo_tabla += "        dataField: \"" + campo[0] + "\",\n"
                    lista_campo_tabla += "        text: \"" + campo_titulo + "\",\n"
                    lista_campo_tabla += "        sort: true,\n"
                    lista_campo_tabla += "        headerStyle: () => { return {width: \"170px\"};}},\n"

                    lista_visualizar += "                  <Row>\n"
                    lista_visualizar += "                      <Col xs={2} className=\"text-muted\">\n"
                    lista_visualizar += "                          " + campo_titulo + ":\n"
                    lista_visualizar += "                      </Col>\n"
                    lista_visualizar += "                      <Col xs={10}>{this.state." + campo[0] + "}</Col>\n"
                    lista_visualizar += "                  </Row>\n"

                    lista_inputs += "            <Col  xs=\"12\" md=\"4\" lg=\"3\">\n"
                    lista_inputs += "               <Form.Label>\n"
                    lista_inputs += "               " + campo_titulo + ":\n"
                    lista_inputs += "                   <OverlayTrigger trigger=\"focus\" placement=\"right\" overlay={popover}>\n"
                    lista_inputs += "                       <Button\n"
                    lista_inputs += "                       variant=\"light\"\n"
                    lista_inputs += "                       onClick={(e) => {\n"

                    este_campo = campo[0]
                    este_tooltip = "Este campo no tiene ayuda."
                    if json_tooltips:
                        if este_campo in json_tooltips:
                            este_tooltip = json_tooltips[este_campo]
                    
                    lista_inputs += "                       this.setState({ input_tooltip: \"" + este_tooltip + "\" });\n"
                    lista_inputs += "                     }}\n"
                    lista_inputs += "                   >\n"
                    lista_inputs += "                       <FontAwesomeIcon icon={faQuestionCircle} />\n"
                    lista_inputs += "                   </Button>\n"
                    lista_inputs += "               </OverlayTrigger>\n"
                    lista_inputs += "            </Form.Label>\n"
                    lista_inputs += "            <Form.Control\n"
                    if "int" in campo[1]:
                        lista_inputs += "              type=\"number\"\n"
                    elif "date" in campo[1]:
                        lista_inputs += "              type=\"date\"\n"
                    elif "decimal" in campo[1]:
                        lista_inputs += "              type=\"number\"\n"
                        lista_inputs += "              step=\"0.01\"\n"
                    else:
                        lista_inputs += "              type=\"text\"\n"
                    
                    lista_inputs += "              name=\"" + campo[0] + "\"\n"
                    lista_inputs += "              value={this.state." + campo[0] + "}\n"
                    lista_inputs += "              onChange={this.onChange" + campo_camel + "}\n"
                    lista_inputs += "            />\n"
                    lista_inputs += "            </Col>\n"

                coma += 1
        cursor.execute("SHOW KEYS FROM " + tabla + " WHERE Key_name = 'PRIMARY';")
        llave_primaria = cursor.fetchall()[0][4]

        #Modelo
        f = open(op_dir + "/plantilla/Model.p_php", "r")
        Modelo_php = f.read()
        f.close()
        Modelo_php = Modelo_php.replace("tabla", tabla)
        Modelo_php = Modelo_php.replace("Singular", Singular)
        Modelo_php = Modelo_php.replace("lista_campos", lista_campos)
        text_file = open(op_dir + "/salida/Modelos/" + Singular + ".php", "w")
        text_file.write(Modelo_php)
        text_file.close()
        print(op_dir + "/salida/Modelos/" + Singular + ".php")

        #Controlador
        f = open(op_dir + "/plantilla/Controlador.p_php", "r")
        Controlador_php = f.read()
        f.close()
        Controlador_php = Controlador_php.replace("Singular", Singular)
        Controlador_php = Controlador_php.replace("singular", singular)
        Controlador_php = Controlador_php.replace("lista_campos_controlador", lista_campos_controlador)
        text_file = open(op_dir + "/salida/Controlador/" + Singular + "Controller.php", "w")
        text_file.write(Controlador_php)
        text_file.close()
        print(op_dir + "/salida/Controlador/" + Singular + "Controller.php")

        #React
        f = open(op_dir + "/plantilla/React.p_js", "r")
        React_js = f.read()
        f.close()
        React_js = React_js.replace("Titulo_Formulario", Titulo_Formulario)
        React_js = React_js.replace("Nombre_Forumulario", Nombre_Forumulario)
        React_js = React_js.replace("Num_Formato", Num_Formato)
        React_js = React_js.replace("url_laravel_api", url_laravel_api)
        React_js = React_js.replace("Singular", Singular)
        React_js = React_js.replace("singular", singular)
        React_js = React_js.replace("Plural", Plural)
        React_js = React_js.replace("plural", plural)
        React_js = React_js.replace("lista_campos_estado_row", lista_campos_estado_row)
        React_js = React_js.replace("lista_campos_estado_nuevo", lista_campos_estado_nuevo)
        React_js = React_js.replace("lista_campo_data", lista_campo_data)
        React_js = React_js.replace("//lista_campo_tabla", lista_campo_tabla)
        React_js = React_js.replace("//lista_on_change", lista_on_change)
        React_js = React_js.replace("lista_visualizar", lista_visualizar)
        React_js = React_js.replace("lista_inputs", lista_inputs)
        React_js = React_js.replace("//lista_campos_estado", lista_campos_estado)
        React_js = React_js.replace("lista_campo_id_data", lista_campo_id_data)
        React_js = React_js.replace("mk_clave_anexo", singular[1:])
        text_file = open(op_dir + "/salida/React/" + Plural + ".js", "w")
        text_file.write(React_js)
        text_file.close()
        print(op_dir + "/salida/React/" + Plural + ".js")

        #Rutas React
        if Plural.startswith('F'):
            App_imports += "import " + Plural + " from \"./formatos/" + Plural + "\";\n"
            App_route += "          <Route exact path=\"/" + plural + "\" component={" + Plural + "} />\n"
            App_route += "          <Route exact path=\"/" + plural + "/ambito/:ambito_id\" component={" + Plural + "} />\n"
        else:
            App_imports += "import " + Plural + " from \"./" + Plural + "\";\n"
            App_route += "          <Route exact path=\"/" + plural + "\" component={" + Plural + "} />\n"

        #Rutas Laravel
        Web_php = Web_org_php
        Web_php = Web_php.replace("Singular", Singular)
        Web_php = Web_php.replace("plural", plural)
        Web_all += Web_php + "\n\n"

f = open(op_dir + "/plantilla/App.p_js", "r")
App_p = f.read()
f.close()
App_p = App_p.replace("//lista_imports_app", App_imports)
App_p = App_p.replace("lista_route_app", App_route)
text_file = open(op_dir + "/salida/App.js", "w")
text_file.write(App_p)
text_file.close()
print(op_dir + "/salida/App.js")

f = open(op_dir + "/plantilla/web_done.p_php", "r")
Web_done = f.read()
f.close()
Web_done = Web_done.replace("lista_rutas", Web_all)

text_file = open(op_dir + "/salida/web.php", "w")
text_file.write(Web_done)
text_file.close()

print(op_dir + "/salida/web.php")
db.close()
