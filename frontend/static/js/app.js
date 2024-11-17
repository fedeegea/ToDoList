// Cargar tareas desde el servidor al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    loadTasks('pending');
    loadTasks('completed');
    document.getElementById('task-form').addEventListener('submit', addTask);
});

// Función para cargar las tareas desde el servidor
async function loadTasks(type) {
    try {
        const response = await fetch('/todos');
        const data = await response.json();

        let tasks;
        if (type === 'pending') {
            tasks = data.pending;
        } else if (type === 'completed') {
            tasks = data.completed;
        } else if (type === 'archived') {
            tasks = data.archived;  // Nueva lista de archivadas
        }

        const taskList = document.getElementById(type === 'pending' ? 'task-list-pending' : type === 'completed' ? 'task-list-completed' : 'task-list-archived');
        taskList.innerHTML = '';

        tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.classList.add('task-item');

            const tags = task.tags ? task.tags.join(', ') : '';
            
            taskElement.innerHTML = `
                <input type="checkbox" ${task.completed ? 'checked' : ''} onclick="toggleTask(${task.id}, '${type}')">
                <span>${task.task}</span>
                <span class="tags">${tags}</span>
                <button class="archive-btn" onclick="archiveTask(${task.id}, '${type}')">
                    <img src="static/icons/archived.png" alt="Archive" style="width: 20px; height: 20px;">
                </button>
                <button class="delete-btn" onclick="deleteTask(${task.id}, '${type}')">Eliminar</button>
                <button class="edit-btn" onclick="editTask(${task.id}, '${type}')">Editar</button>
            `;


            taskList.appendChild(taskElement);
        });
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}


// Mostrar tareas pendientes
function showPendingTasks() {
    document.getElementById('pending-section').style.display = 'block';
    document.getElementById('completed-section').style.display = 'none';
    loadTasks('pending');
}

// Mostrar tareas completadas
function showCompletedTasks() {
    document.getElementById('completed-section').style.display = 'block';
    document.getElementById('pending-section').style.display = 'none';
    loadTasks('completed');
}

// Agregar una nueva tarea
async function addTask(event) {
    event.preventDefault();
    const taskInput = document.getElementById('task-input');
    const tagsInput = document.getElementById('tags-input');
    
    if (taskInput.value.trim() !== '') {  // Asegurarse de que no se agregue tarea vacía
        const tags = tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);  // Obtener etiquetas

        const newTask = { 
            task: taskInput.value,
            tags: tags  // Incluir etiquetas
        };

        try {
            const response = await fetch('/todos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newTask)
            });

            if (response.ok) {
                loadTasks('pending');  // Recargar tareas pendientes desde el servidor
                taskInput.value = '';  // Limpiar el campo de entrada
                tagsInput.value = '';  // Limpiar el campo de etiquetas
            } else {
                console.error('Error adding task:', await response.json());
            }
        } catch (error) {
            console.error('Error adding task:', error);
        }
    }
}

// Filtrar tareas por etiqueta
async function filterTasksByTag() {
    const tagFilter = document.getElementById('tag-filter').value.trim();
    
    if (tagFilter) {
        try {
            const response = await fetch(`/todos/filter?tag=${tagFilter}`);
            const data = await response.json();

            if (response.ok) {
                const taskList = document.getElementById('task-list-pending');
                taskList.innerHTML = '';  // Limpiar el contenedor de tareas pendientes

                data.tasks.forEach(task => {
                    const taskElement = document.createElement('div');
                    taskElement.classList.add('task-item');
                    taskElement.innerHTML = `
                        <input type="checkbox" ${task.completed ? 'checked' : ''} onclick="toggleTask(${task.id}, 'pending')">
                        <span>${task.task}</span>
                        <button class="delete-btn" onclick="deleteTask(${task.id}, 'pending')">Eliminar</button>
                    `;
                    taskList.appendChild(taskElement);
                });
            } else {
                console.error('Error filtering tasks:', await response.json());
            }
        } catch (error) {
            console.error('Error filtering tasks:', error);
        }
    }
}

// Marcar una tarea como completada o desmarcar
async function toggleTask(taskId, type) {
    try {
        await fetch(`/todos/${taskId}/complete`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        loadTasks(type);  // Recargar tareas pendientes/completadas desde el servidor
    } catch (error) {
        console.error('Error toggling task:', error);
    }
}

// Eliminar una tarea
async function deleteTask(taskId, type) {
    try {
        const response = await fetch(`/todos/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTasks(type);  // Recargar tareas pendientes/completadas desde el servidor
        } else {
            console.error('Error deleting task:', await response.json());
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// Función para editar una tarea
async function editTask(taskId, type) {
    const taskInput = prompt("Editar tarea:", "");
    if (taskInput !== null && taskInput.trim() !== "") {
        const tagsInput = prompt("Editar etiquetas (separadas por comas):", "");
        const tags = tagsInput ? tagsInput.split(',').map(tag => tag.trim()) : [];

        const updatedTask = { 
            task: taskInput,
            tags: tags
        };

        try {
            const response = await fetch(`/todos/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updatedTask)
            });

            if (response.ok) {
                loadTasks(type);  // Recargar tareas desde el servidor
            } else {
                console.error('Error editing task:', await response.json());
            }
        } catch (error) {
            console.error('Error editing task:', error);
        }
    }
}

function toggleArchivedTasks() {
    const archivedSection = document.getElementById('archived-section');
    const toggleBtn = document.getElementById('toggle-archived-btn');

    if (archivedSection.style.display === 'block') {
        // Si ya se están mostrando las archivadas, ocultarlas
        archivedSection.style.display = 'none';
        toggleBtn.innerText = 'Mostrar Archivadas';
    } else {
        // Si están ocultas, mostrarlas
        archivedSection.style.display = 'block';
        toggleBtn.innerText = 'Ocultar Archivadas';
        loadTasks('archived');  // Cargar tareas archivadas si no están visibles
    }
}

function showArchivedTasks() {
    document.getElementById('archived-section').style.display = 'block';
    document.getElementById('pending-section').style.display = 'none';
    document.getElementById('completed-section').style.display = 'none';
    loadTasks('archived');  // Llama a loadTasks con tipo 'archived'
}

async function archiveTask(taskId, type) {
    try {
        const response = await fetch(`/todos/${taskId}/archive`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            loadTasks(type); // Recargar tareas actualizadas
        } else {
            console.error('Error archiving task:', await response.json());
        }
    } catch (error) {
        console.error('Error archiving task:', error);
    }
}

