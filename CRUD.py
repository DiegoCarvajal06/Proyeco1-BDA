from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from bson.errors import InvalidId  # Correcta importación de InvalidId


def conectar_bd():
    uri = "mongodb://localhost:27017/"
    try:
        cliente = MongoClient(uri)
        cliente.admin.command('ping')
        return cliente
    except ConnectionFailure as e:
        print(f"Error al conectar a la base de datos MongoDB: {e}")
        return None

def insertar_documento(coleccion):
    documento = {}
    campos = int(input("¿Cuántos campos tendrá el documento? "))
    for i in range(campos):
        campo = input(f"Nombre del campo {i + 1}: ")
        valor = input(f"Valor del campo {campo}: ")
        documento[campo] = valor
    resultado = coleccion.insert_one(documento)
    print(f"Documento insertado, ID: {resultado.inserted_id}")

def listar_documentos(coleccion):
    documentos = coleccion.find()
    print("Documentos en la colección:")
    for documento in documentos:
        print(documento)

def actualizar_documento(coleccion):
    documento_id = input("Ingrese el ID del documento a actualizar: ")
    try:
        oid = ObjectId(documento_id)
        campo = input("¿Qué campo quieres actualizar? ")
        nuevo_valor = input("Nuevo valor para el campo: ")
        resultado = coleccion.update_one({"_id": oid}, {"$set": {campo: nuevo_valor}})
        if resultado.modified_count > 0:
            print("Documento actualizado correctamente.")
        else:
            print("No se actualizó ningún documento.")
    except InvalidId:
        print("ID de documento inválido. Asegúrese de que el ID está en formato correcto.")

def eliminar_documento(coleccion):
    documento_id = input("Ingrese el ID del documento a eliminar: ")
    try:
        resultado = coleccion.delete_one({"_id": ObjectId(documento_id)})
        if resultado.deleted_count > 0:
            print("Documento eliminado correctamente.")
        else:
            print("No se eliminó ningún documento.")
    except InvalidId:
        print("ID de documento inválido. Asegúrese de que el ID está en formato correcto.")

def menu_crud(coleccion):
    opciones = {
        '1': insertar_documento,
        '2': listar_documentos,
        '3': actualizar_documento,
        '4': eliminar_documento
    }
    
    while True:
        print("\nMenú CRUD MongoDB")
        print("1. Insertar documento")
        print("2. Listar documentos")
        print("3. Actualizar documento")
        print("4. Eliminar documento")
        print("5. Salir al menú de colecciones")
        opcion = input("Seleccione una opción: ")

        if opcion == '5':
            break
        elif opcion in opciones:
            opciones[opcion](coleccion)
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

def menu():
    conexion = conectar_bd()
    if not conexion:
        print("No se pudo conectar a MongoDB. Saliendo...")
        return
    db = conexion['herencias']
    print("Conexión exitosa a MongoDB!")

    while True:
        colecciones = db.list_collection_names()
        print(f"¿En qué colección deseas trabajar? {colecciones}")
        coleccion_nombre = input("Nombre de la colección o 'salir' para terminar: ")
        if coleccion_nombre.lower() == 'salir':
            print("Saliendo del programa...")
            break
        if coleccion_nombre in colecciones:
            coleccion = db[coleccion_nombre]
            menu_crud(coleccion)
        else:
            print("Colección no encontrada. Por favor, intente de nuevo.")

if __name__ == "__main__":
    menu()















'''
@app.route('/collection/<nombre>', methods=['GET', 'POST'])
def manage_collection(nombre):
    db = conectar_bd()
    collection = db[nombre]
    document_fields = collection.find_one()  # Obtener campos de ejemplo para construir el formulario
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Agregar':
            # Crear un nuevo documento a partir de los datos del formulario, excluyendo el 'action'
            documento = {k: v for k, v in request.form.items() if k != 'action' and v.strip()}
            # Verificar que todos los campos requeridos estén completos, excepto el ID
            if all(documento.get(key) for key in document_fields if key != '_id'):
                # Insertar el documento en la colección
                resultado = collection.insert_one(documento)
                flash(f"Documento agregado con éxito, ID: {resultado.inserted_id}", 'success')
            else:
                flash("Debe llenar todos los campos requeridos.", 'error')

        elif action == 'Actualizar':
            # Obtener el ID del documento a actualizar y los datos a actualizar
            documento_id = request.form.get('_id')
            cambios = {k: v for k, v in request.form.items() if k != 'action' and k != '_id' and request.form.get('check_' + k)}
            if documento_id and cambios:
                # Actualizar el documento en la colección
                resultado = collection.update_one({'_id': ObjectId(documento_id)}, {'$set': cambios})
                if resultado.modified_count:
                    flash("Documento actualizado correctamente.", 'success')
                else:
                    flash("No se actualizó ningún documento.", 'error')
            else:
                flash("Debe proporcionar un ID válido y seleccionar los campos a actualizar.", 'error')

        elif action == 'Eliminar':
            # Obtener el ID del documento a eliminar
            documento_id = request.form.get('_id')
            if documento_id:
                # Eliminar el documento de la colección
                resultado = collection.delete_one({'_id': ObjectId(documento_id)})
                if resultado.deleted_count:
                    flash("Documento eliminado correctamente.", 'success')
                else:
                    flash("No se encontró el documento a eliminar.", 'error')
            else:
                flash("Debe proporcionar un ID válido para eliminar.", 'error')

        elif action == 'Consultar':
            # Obtener el ID del documento a consultar
            documento_id = request.form.get('_id')
            if documento_id:
                # Buscar el documento en la colección
                documento = collection.find_one({'_id': ObjectId(documento_id)})
                if documento:
                    return render_template('collection_template.html', fields=documento, nombre_coleccion=nombre, modo='consultar')
                else:
                    flash("No se encontró el documento.", 'error')
            else:
                flash("Debe proporcionar un ID válido para consultar.", 'error')

        elif action == 'Ver Todo':
            # Mostrar todos los documentos de la colección
            documentos = list(collection.find())
            return render_template('collection_template.html', documentos=documentos, nombre_coleccion=nombre, modo='ver_todo')

        elif action == 'Salir':
            return redirect(url_for('dashboard'))

    return render_template('collection_management.html', fields=document_fields if document_fields else {}, nombre_coleccion=nombre)

'''