function createDocument() {
    var data = prompt("Ingrese los datos como JSON (ej: {'nombre': 'Juan'})");
    fetch('/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: data
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseArea').innerText = "Creación exitosa: " + JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error:', error));
}

function readDocuments() {
    fetch('/read')
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseArea').innerText = JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error:', error));
}


function updateDocument() {
    var id = prompt("Ingrese el ID del documento a actualizar");
    var data = prompt("Ingrese los nuevos datos como JSON (ej: {'nombre': 'Ana'})");
    fetch(`/update/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: data
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseArea').innerText = "Actualización exitosa: " + JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error:', error));
}

function deleteDocument() {
    var id = prompt("Ingrese el ID del documento a eliminar");
    fetch(`/delete/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('responseArea').innerText = "Eliminación exitosa: " + JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error:', error));
}
