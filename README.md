# Aplicación To-Do

Una aplicación de lista de tareas con backend en Flask y base de datos MySQL. Permite agregar, editar, eliminar y archivar tareas. El frontend está construido con HTML, CSS y JavaScript.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Instalación](#instalación)
- [Uso](#uso)
- [Licencia](#licencia)

## Descripción

Esta es una aplicación para gestionar tareas de forma sencilla. Los usuarios pueden agregar nuevas tareas, marcarlas como completadas, editarlas, eliminarlas o archivarlas. 

El backend está desarrollado con Flask y se conecta a una base de datos MySQL para almacenar las tareas. El frontend está hecho con HTML, CSS y JavaScript para crear una interfaz de usuario amigable.

### Características:
- Crear tareas nuevas
- Editar tareas existentes
- Eliminar tareas
- Marcar tareas como completadas
- Archivar tareas completadas
- Iconos visuales para las acciones

## Instalación

Para ejecutar esta aplicación en tu entorno local, sigue los pasos a continuación.

### Requisitos previos

- Python 3.x
- MySQL 5.7+
- Flask 2.x
- Dependencias listadas en `requirements.txt`

### Pasos de instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/ensolvers-github-challenges/Egea-312a72.git
    ```
2. Accede a la carpeta del proyecto:
    ```bash
    cd Egea-312a72
    ```
3. Accede a la carpeta `backend`:
    ```bash
    cd backend
    ```
4. Crea un entorno virtual:
    ```bash
    python3 -m venv venv
    ```
5. Activa el entorno virtual:
    - En macOS/Linux:
      ```bash
      source venv/bin/activate
      ```
    - En Windows:
      ```bash
      venv\Scripts\activate
      ```
6. Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```
7. Configura la base de datos MySQL:

    Conéctate a tu base de datos MySQL y ejecuta los siguientes comandos para crear la base de datos y las tablas necesarias:

    ```sql
    CREATE DATABASE todo_db;

    USE todo_db;

    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    );

    INSERT INTO users (username, password) 
    VALUES ('user', '1234');

    CREATE TABLE IF NOT EXISTS todos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task VARCHAR(255) NOT NULL,
        completed BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    CREATE TABLE tags (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    );

    CREATE TABLE task_tags (
        task_id INT,
        tag_id INT,
        FOREIGN KEY (task_id) REFERENCES todos(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id),
        PRIMARY KEY (task_id, tag_id)
    );

    ALTER TABLE task_tags
    DROP FOREIGN KEY task_tags_ibfk_1;

    ALTER TABLE task_tags
    ADD CONSTRAINT task_tags_ibfk_1
    FOREIGN KEY (task_id) REFERENCES todos(id)
    ON DELETE CASCADE;

    ALTER TABLE todos ADD archived BOOLEAN DEFAULT FALSE;
    ```

8. Ejecuta la aplicación Flask:
    ```bash
    python app.py
    ```

## Uso

Una vez que hayas instalado y configurado el proyecto, puedes iniciar la aplicación.

1. Ejecuta el servidor Flask:
    ```bash
    python backend/app.py
    ```
2. Abre tu navegador y visita `http://localhost:5000` para interactuar con la aplicación.

### Cómo ejecutar el script

1. **Crear el archivo `run.sh`** en tu entorno de desarrollo (idealmente en sistemas basados en UNIX como macOS o Linux):
    ```bash
    touch run.sh
    ```

2. **Añadir el contenido del script**:

   ```bash
   #!/bin/bash
   
   # Instalar dependencias de Python
   echo "Instalando dependencias de Python..."
   pip install -r requirements.txt

   # Crear y configurar la base de datos
   echo "Configurando la base de datos..."
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS todo_db;"
   mysql -u root -p todo_db < backend/db/schema.sql

   # Iniciar la aplicación Flask
   echo "Iniciando la aplicación Flask..."
   python backend/app.py

2. **Hacer el script ejecutable: En sistemas como macOS o Linux, ejecuta el siguiente comando en la terminal para hacer el script ejecutable**:

    chmod +x run.sh

3. **Ejecutar el script: Ejecuta el script con el siguiente comando**:

    ./run.sh

## Login

Los usuarios puedan acceder usando las credenciales predeterminadas. 

### Credenciales predeterminadas:

- **Usuario**: `user`
- **Contraseña**: `1234`

Estas credenciales permiten acceder a la aplicación después de configurar correctamente la base de datos.


## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.