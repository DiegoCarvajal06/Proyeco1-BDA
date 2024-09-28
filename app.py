from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId
from conectarBD import conectar_bd

app = Flask(__name__)
app.secret_key = 'tu_super_secreto'
app.config['SESSION_TYPE'] = 'filesystem'

# Lista para guardar usuarios
usuarios = []

## FUnciones de Login y regustrarse
@app.route('/')
def index():
    if 'nombre_usuario' in session:
        # Mensaje de bienvenida y opciones de colección
        return render_template('dashboard.html', nombre_usuario=session['nombre_usuario'])
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        for usuario in usuarios:
            if usuario['nombre_usuario'] == nombre_usuario and check_password_hash(usuario['password'], password):
                session['nombre_usuario'] = usuario['nombre_usuario']
                session['tipo_usuario'] = usuario['tipo_usuario']
                return redirect(url_for('index'))
        flash('Usuario o contraseña inválidos')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        password = request.form['password']
        tipo_usuario = request.form['tipo_usuario']

        # Verificar si el usuario ya existe
        for usuario in usuarios:
            if usuario['nombre_usuario'] == nombre_usuario:
                flash('El nombre de usuario ya existe')
                return redirect(url_for('register'))

        # Guardar el nuevo usuario
        usuarios.append({
            'nombre_usuario': nombre_usuario,
            'password': generate_password_hash(password),
            'tipo_usuario': tipo_usuario
        })
        flash('Usuario registrado correctamente')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('nombre_usuario', None)
    flash('Sesión cerrada')
    return redirect(url_for('login'))


#MAnejo de colleciones 

def handle_collection_actions(nombre):
    db = conectar_bd()
    collection = db[nombre]
    document_fields = collection.find_one()  # Asegúrate de gestionar None si no hay documentos
    if request.method == 'POST':
        action = request.form.get('action')
        # Implementa la lógica de las acciones aquí, como agregar, actualizar, etc.
        # Utiliza 'flash()' para mensajes y 'redirect()' para redirigir según sea necesario
    # Pasa variables necesarias a la plantilla
    return render_template('manage_collection.html', fields=document_fields, nombre_coleccion=nombre)


@app.route('/herencias/festividades', methods=['GET', 'POST'])
def manage_festividades():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_festividades'))
    
    db = client['herencias']
    collection = db['Festividades']
    
    document_fields = collection.find_one()  # Encuentra el primer documento en la colección.

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            # Verificar si document_fields es None antes de intentar acceder a .keys()
            if document_fields and all(documento.get(key) for key in document_fields.keys() if key != '_id'):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('check_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)}) if documento_id else None
            if documento:
                return render_template('manage_festividades.html', documento=documento)
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_festividades.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    return render_template('manage_festividades.html', fields=document_fields if document_fields else {}, nombre_coleccion='Festividades')

'''
@app.route('/herencias/festividades', methods=['GET', 'POST'])
def manage_festividades():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_festividades'))  # Asegúrate de que esta redirección tenga sentido.
    
    db = client['herencias']
    collection = db['Festividades']
    
    document_fields = collection.find_one()  # Encuentra el primer documento en la colección.

    # Siempre cargar la página, incluso si no hay documentos.
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            if all(documento.get(key) for key in document_fields.keys() if key != '_id'):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('check_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)}) if documento_id else None
            if documento:
                return render_template('manage_festividades.html', documento=documento)
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_festividades.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))
            
    # Proporciona un documento vacío si no se encontró ninguno
    return render_template('manage_festividades.html', fields=document_fields if document_fields else {}, nombre_coleccion='Festividades')


####
@app.route('/herencias/festividades', methods=['GET', 'POST'])
def manage_festividades():
    client = conectar_bd()
    if not client:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('manage_festividades'))
    
    db = client['herencias']  # Asegúrate de tener el nombre correcto de tu base de datos aquí
    collection = db['Festividades']
    
    document_fields = collection.find_one()  # Esto debe funcionar ahora, asegúrate de tener documentos en la colección
    if not document_fields:
        flash('No hay documentos en la colección festividades.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if request.method == 'POST':
            action = request.form.get('action')

        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            if all(documento.get(key) for key in document_fields if key != '_id'):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('check_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)}) if documento_id else None
            if documento:
                return render_template('manage_festividades.html', documento=documento)
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_festividades.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))



    return render_template('manage_festividades.html', fields=document_fields if document_fields else {}, nombre_coleccion='festividades')

####

@app.route('/festividades', methods=['GET', 'POST'])
def manage_festividades():
    db = conectar_bd()
    collection = db['festividades']
    document_fields = collection.find_one()  # Obtener un documento para usar como ejemplo

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Agregar':
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            if all(documento.get(key) for key in document_fields if key != '_id'):
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('check_' + k)}
            if documento_id and cambios:
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                flash("Documento actualizado correctamente." if resultado.modified_count else "No se actualizó ningún documento.", 'success' if resultado.modified_count else 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            documento_id = request.form.get('_id')
            if documento_id:
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                flash("Documento eliminado correctamente." if resultado.deleted_count else "No se encontró el documento a eliminar.", 'success' if resultado.deleted_count else 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            documento_id = request.form.get('_id')
            documento = collection.find_one({'_id': ObjectId(documento_id)}) if documento_id else None
            if documento:
                return render_template('manage_festividades.html', documento=documento)
            else:
                flash("No se encontró el documento.", 'error')

        elif action == 'Ver Todo':
            documentos = list(collection.find())
            return render_template('manage_festividades.html', documentos=documentos, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('index'))

    # Preparar los campos para un formulario vacío inicialmente
    campos_vacios = {key: '' for key in document_fields if key != '_id'}
    return render_template('manage_festividades.html', campos=campos_vacios)

'''

@app.route('/herencias/ingredientes', methods=['GET', 'POST'])
def manage_ingredientes():
    return handle_collection_actions('ingredientes')

@app.route('/collection/poblaciones', methods=['GET', 'POST'])
def manage_poblaciones():
    return handle_collection_actions('poblaciones')

@app.route('/collection/recetas', methods=['GET', 'POST'])
def manage_recetas():
    return handle_collection_actions('recetas')






if __name__ == '__main__':
    app.run(debug=True)



'''
@app.route('/coleccion/<nombre>', methods=['GET'])
def crud(nombre):
    return render_template('crud.html', nombre_coleccion=nombre)


@app.route('/coleccion/<nombre>/gestion', methods=['GET', 'POST'])
def gestion_coleccion(nombre):
    db = conectar_bd()
    coleccion = db[nombre]

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'insertar':
            datos = {k: v for k, v in request.form.items() if k not in ['action']}
            coleccion.insert_one(datos)
            flash(f"Documento insertado en {nombre}")

        elif action == 'consultar':
            documento_id = request.form.get('documento_id')
            documento = coleccion.find_one({'_id': ObjectId(documento_id)})
            return render_template(f'{nombre}_gestion.html', documento=documento, nombre_coleccion=nombre)

        elif action == 'actualizar':
            documento_id = request.form.get('documento_id')
            datos = {k: v for k, v in request.form.items() if k not in ['action', 'documento_id']}
            coleccion.update_one({'_id': ObjectId(documento_id)}, {'$set': datos})
            flash("Documento actualizado")

        elif action == 'eliminar':
            documento_id = request.form.get('documento_id')
            coleccion.delete_one({'_id': ObjectId(documento_id)})
            flash("Documento eliminado")

    return render_template(f'{nombre}_gestion.html', nombre_coleccion=nombre)



@app.route('/coleccion/<nombre>/insertar', methods=['GET', 'POST'])
def insertar_documento(nombre):
    db = conectar_bd()
    coleccion = db[nombre]
    if request.method == 'POST':
        # Recoge todos los campos del formulario, excepto los de control como botones o acciones.
        documento = {key: request.form[key] for key in request.form if key not in ['action', 'submit']}
        resultado = coleccion.insert_one(documento)
        flash(f"Documento insertado, ID: {resultado.inserted_id}")
        return redirect(url_for('coleccion', nombre=nombre))
    return render_template('insertar_documento.html', nombre_coleccion=nombre)

@app.route('/coleccion/<nombre>/listar')
def listar_documentos(nombre):
    db = conectar_bd()
    coleccion = db[nombre]
    documentos = list(coleccion.find())
    return render_template('colecciones.html', documentos=documentos, nombre_coleccion=nombre)

@app.route('/coleccion/<nombre>/actualizar', methods=['GET', 'POST'])
def actualizar_documento(nombre):
    db = conectar_bd()
    coleccion = db[nombre]
    if request.method == 'POST':
        documento_id = request.form['documento_id']
        cambios = {key: request.form[key] for key in request.form if key not in ['documento_id', 'action', 'submit']}
        coleccion.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
        flash("Documento actualizado correctamente")
        return redirect(url_for('listar_documentos', nombre=nombre))
    # Aquí puedes agregar código para mostrar un formulario de actualización si es GET.
    return render_template('actualizar_documento.html', nombre_coleccion=nombre)

@app.route('/coleccion/<nombre>/eliminar', methods=['POST'])
def eliminar_documento(nombre):
    db = conectar_bd()
    coleccion = db[nombre]
    documento_id = request.form['documento_id']
    coleccion.delete_one({'_id': ObjectId(documento_id)})
    flash("Documento eliminado correctamente")
    return redirect(url_for('listar_documentos', nombre=nombre))



###5




@app.route('/coleccion/ingredientes', methods=['GET'])
def gestion_ingredientes():
    return render_template('ingredientes.html')

@app.route('/coleccion/ingredientes/consultar', methods=['POST'])
def consultar_ingrediente():
    id = request.form['id']
    db = conectar_bd()
    documento = db['ingredientes'].find_one({'_id': ObjectId(id)})
    return render_template('ingredientes.html', ingrediente=documento)

@app.route('/coleccion/ingredientes/actualizar_agregar', methods=['POST'])
def actualizar_agregar_ingrediente():
    db = conectar_bd()
    datos = {k: v for k, v in request.form.items() if k != 'id'}
    if request.form['id']:  # Si tiene ID, actualizamos
        db['ingredientes'].update_one({'_id': ObjectId(request.form['id'])}, {'$set': datos})
    else:  # Si no tiene ID, agregamos
        db['ingredientes'].insert_one(datos)
    return redirect(url_for('gestion_ingredientes'))

@app.route('/coleccion/ingredientes/eliminar', methods=['POST'])
def eliminar_ingrediente():
    db = conectar_bd()
    db['ingredientes'].delete_one({'_id': ObjectId(request.form['id'])})
    return redirect(url_for('gestion_ingredientes'))



@app.route('/coleccion/<nombre>/listar')
def listar_documentos(nombre):
    db = conectar_bd()
    if db:
        coleccion = db[nombre]
        documentos = list(coleccion.find())
        return render_template('listar_documentos.html', documentos=documentos, nombre_coleccion=nombre)
    else:
        flash("Error de conexión a la base de datos.")
        return redirect(url_for('index'))


@app.route('/coleccion/<nombre>/buscar', methods=['GET', 'POST'])
def buscar_documento(nombre):
    db = conectar_bd()
    if db:
        coleccion = db[nombre]
        if request.method == 'POST':
            documento_id = request.form['documento_id']
            try:
                documento = coleccion.find_one({"_id": ObjectId(documento_id)})
                if documento:
                    return render_template('mostrar_documento.html', documento=documento, nombre_coleccion=nombre)
                else:
                    flash("No se encontró el documento.")
                    return redirect(url_for('buscar_documento', nombre=nombre))
            except InvalidId:
                flash("ID inválido proporcionado.")
                return redirect(url_for('buscar_documento', nombre=nombre))
        return render_template('buscar_documento.html', nombre_coleccion=nombre)
    else:
        flash("No se pudo conectar a la base de datos.")
        return redirect(url_for('index'))


@app.route('/coleccion/<nombre>/actualizar', methods=['GET', 'POST'])
def actualizar_documento(nombre):
    db = conectar_bd()
    coleccion = db[nombre]
    if request.method == 'POST':
        documento_id = request.form['documento_id']
        campo = request.form['campo']
        nuevo_valor = request.form['nuevo_valor']
        resultado = coleccion.update_one({"_id": ObjectId(documento_id)}, {"$set": {campo: nuevo_valor}})
        if resultado.modified_count > 0:
            flash("Documento actualizado correctamente.")
        else:
            flash("No se actualizó ningún documento.")
        return redirect(url_for('listar_documentos', nombre=nombre))
    return render_template('actualizar_documento.html', nombre_coleccion=nombre)

@app.route('/coleccion/<nombre>/eliminar', methods=['POST'])
def eliminar_documento(nombre):
    db = conectar_bd()
    coleccion = db[nombre]
    documento_id = request.form['documento_id']
    resultado = coleccion.delete_one({"_id": ObjectId(documento_id)})
    if resultado.deleted_count > 0:
        flash("Documento eliminado correctamente.")
    else:
        flash("No se eliminó ningún documento.")
    return redirect(url_for('listar_documentos', nombre=nombre))
'''
    
