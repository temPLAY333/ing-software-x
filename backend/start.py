#!/usr/bin/env python3
"""
Script de inicio del backend que:
1. Espera a que MongoDB esté disponible
2. Inicializa la base de datos (colecciones e índices)
3. Opcionalmente inserta datos de prueba
4. Inicia la aplicación Flask
"""

import os
import sys
import time
import subprocess
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def wait_for_mongodb(max_retries=30, retry_interval=2):
    """Espera a que MongoDB esté disponible"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017/main_db')
    print(f"🔄 Esperando a que MongoDB esté disponible en {mongodb_uri}...")
    
    for i in range(max_retries):
        try:
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
            # Forzar conexión
            client.admin.command('ping')
            client.close()
            print("✅ MongoDB está disponible")
            return True
        except ConnectionFailure:
            print(f"⏳ Intento {i + 1}/{max_retries} - MongoDB no disponible aún...")
            time.sleep(retry_interval)
    
    print("❌ No se pudo conectar a MongoDB después de varios intentos")
    return False

def initialize_database():
    """Inicializa la base de datos ejecutando init_db.py"""
    print("\n🚀 Inicializando base de datos...")
    
    # Determinar si se deben insertar datos de prueba
    # Configurable vía variable de entorno INIT_DB_WITH_SAMPLE_DATA
    insert_sample = os.getenv('INIT_DB_WITH_SAMPLE_DATA', 'true').lower() == 'true'
    
    try:
        cmd = [sys.executable, 'init_db.py']
        if insert_sample:
            cmd.append('--with-sample-data')
            print("📝 Insertando datos de prueba...")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ Base de datos inicializada correctamente")
            return True
        else:
            print("⚠️ Hubo un problema en la inicialización")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando init_db.py: {e}")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def start_flask_app():
    """Inicia la aplicación Flask"""
    print("\n🌟 Iniciando aplicación Flask...")
    print("=" * 60)
    
    try:
        # Ejecutar app.py
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    print("=" * 60)
    print("🐍 BACKEND FLASK - Script de Inicio")
    print("=" * 60)
    
    # 1. Esperar a MongoDB
    if not wait_for_mongodb():
        sys.exit(1)
    
    # 2. Inicializar base de datos
    # Solo inicializar si SKIP_DB_INIT no está en 'true'
    skip_init = os.getenv('SKIP_DB_INIT', 'false').lower() == 'true'
    
    if not skip_init:
        if not initialize_database():
            print("⚠️ Continuando a pesar del error en la inicialización...")
    else:
        print("⏭️  Saltando inicialización de base de datos (SKIP_DB_INIT=true)")
    
    # 3. Iniciar aplicación
    start_flask_app()

if __name__ == '__main__':
    main()
