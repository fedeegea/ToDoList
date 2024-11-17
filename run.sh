#!/bin/bash

# Paso 1: Verificar si las dependencias de Python están instaladas
echo "Instalando dependencias de Python..."
pip install -r requirements.txt

# Paso 2: Configuración de la base de datos
echo "Configurando la base de datos..."

# Comando para crear la base de datos (solo si no existe)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS todo_db;"

# Crear las tablas y poblar la base de datos
mysql -u root -p todo_db < backend/db/schema.sql

# Paso 3: Iniciar la aplicación Flask
echo "Iniciando la aplicación Flask..."
python backend/app.py
