"""
Script de Inicialización de Base de Datos MongoDB

Este script:
1. Conecta a MongoDB Atlas
2. Crea las colecciones necesarias
3. Crea índices
4. (Opcional) Inserta datos de prueba

Uso:
    python init_db.py
    python init_db.py --with-sample-data
"""

import os
import sys
from dotenv import load_dotenv
from mongoengine import connect, disconnect
import argparse

# Cargar variables de entorno
load_dotenv()

# Importar modelos
from models import Usuario, Mensaje, MensajePrivado, Etiqueta, Mencion

def connect_db():
    """Conecta a MongoDB Atlas"""
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise ValueError("MONGODB_URI no está configurado en .env")
        
        # Conectar a la base de datos principal
        connect(
            db='main_db',
            host=mongodb_uri,
            alias='default',
            tls=True,
            tlsAllowInvalidCertificates=False
        )
        print("✅ Conectado a MongoDB Atlas (main_db)")
        
        # Conectar a la base de datos de logs
        mongodb_logs_uri = os.getenv('MONGODB_LOGS_URI')
        if mongodb_logs_uri:
            connect(
                db='logs_db',
                host=mongodb_logs_uri,
                alias='logs',
                tls=True,
                tlsAllowInvalidCertificates=False
            )
            print("✅ Conectado a MongoDB Atlas (logs_db)")
        
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return False

def create_collections():
    """Crea las colecciones y sus índices"""
    try:
        print("\n📦 Creando colecciones e índices...")
        
        # Las colecciones se crean automáticamente al insertar el primer documento
        # Pero podemos asegurar que los índices existan
        
        # Usuario
        Usuario.ensure_indexes()
        print("✅ Colección 'usuarios' e índices creados")
        
        # Etiqueta
        Etiqueta.ensure_indexes()
        print("✅ Colección 'etiquetas' e índices creados")
        
        # Mencion
        Mencion.ensure_indexes()
        print("✅ Colección 'menciones' e índices creados")
        
        # Mensaje
        Mensaje.ensure_indexes()
        print("✅ Colección 'mensajes' e índices creados")
        
        # MensajePrivado
        MensajePrivado.ensure_indexes()
        print("✅ Colección 'mensajes_privados' e índices creados")
        
        return True
    except Exception as e:
        print(f"❌ Error creando colecciones: {e}")
        return False

def insert_sample_data():
    """Inserta datos de prueba"""
    try:
        print("\n📝 Insertando datos de prueba...")
        
        # Limpiar datos existentes (solo en desarrollo)
        Usuario.objects.delete()
        Etiqueta.objects.delete()
        Mencion.objects.delete()
        Mensaje.objects.delete()
        MensajePrivado.objects.delete()
        print("🗑️  Datos anteriores eliminados")
        
        # Crear usuarios
        usuario1 = Usuario(
            nickName="juanperez",
            nombre="Juan",
            apellido="Pérez",
            mail="juan@example.com",
            biografia="Desarrollador Full Stack",
            rol="user"
        )
        usuario1.set_password("password123")
        usuario1.save()
        print(f"✅ Usuario creado: {usuario1.nickName}")
        
        usuario2 = Usuario(
            nickName="mariagarcia",
            nombre="María",
            apellido="García",
            mail="maria@example.com",
            biografia="Diseñadora UX/UI",
            rol="user"
        )
        usuario2.set_password("password123")
        usuario2.save()
        print(f"✅ Usuario creado: {usuario2.nickName}")
        
        usuario3 = Usuario(
            nickName="admin",
            nombre="Admin",
            apellido="System",
            mail="admin@example.com",
            biografia="Administrador del sistema",
            rol="admin"
        )
        usuario3.set_password("admin123")
        usuario3.save()
        print(f"✅ Usuario creado: {usuario3.nickName}")
        
        # Crear etiquetas
        etiqueta1 = Etiqueta(texto="#python").save()
        etiqueta2 = Etiqueta(texto="#angular").save()
        etiqueta3 = Etiqueta(texto="#mongodb").save()
        print("✅ Etiquetas creadas: #python, #angular, #mongodb")
        
        # Crear menciones
        mencion1 = Mencion(usuario=usuario2).save()
        mencion2 = Mencion(usuario=usuario3).save()
        print(f"✅ Menciones creadas: @{usuario2.nickName}, @{usuario3.nickName}")
        
        # Crear mensaje público
        mensaje1 = Mensaje(
            texto="¡Hola @mariagarcia! ¿Qué tal el proyecto? #python #mongodb",
            autor=usuario1,
            etiquetas=[etiqueta1, etiqueta3],
            menciones=[mencion1]
        )
        mensaje1.save()
        print(f"✅ Mensaje público creado por {usuario1.nickName}")
        
        # Crear otro mensaje
        mencion3 = Mencion(usuario=usuario1).save()
        mensaje2 = Mensaje(
            texto="¡Muy bien @juanperez! El diseño está quedando genial #angular",
            autor=usuario2,
            etiquetas=[etiqueta2],
            menciones=[mencion3]
        )
        mensaje2.save()
        print(f"✅ Mensaje público creado por {usuario2.nickName}")
        
        # Crear mensajes privados
        mensaje_privado1 = MensajePrivado(
            texto="Hola María, ¿podemos hablar sobre el proyecto?",
            emisor=usuario1,
            receptor=usuario2
        )
        mensaje_privado1.save()
        print(f"✅ Mensaje privado de {usuario1.nickName} → {usuario2.nickName}")
        
        mensaje_privado2 = MensajePrivado(
            texto="¡Claro! Dime, ¿qué necesitas?",
            emisor=usuario2,
            receptor=usuario1
        )
        mensaje_privado2.save()
        mensaje_privado2.marcar_como_leido()
        print(f"✅ Mensaje privado de {usuario2.nickName} → {usuario1.nickName}")
        
        print("\n✅ Datos de prueba insertados correctamente")
        print("\n📊 Resumen:")
        print(f"   - Usuarios: {Usuario.objects.count()}")
        print(f"   - Etiquetas: {Etiqueta.objects.count()}")
        print(f"   - Menciones: {Mencion.objects.count()}")
        print(f"   - Mensajes públicos: {Mensaje.objects.count()}")
        print(f"   - Mensajes privados: {MensajePrivado.objects.count()}")
        
        return True
    except Exception as e:
        print(f"❌ Error insertando datos de prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Inicializar base de datos MongoDB')
    parser.add_argument('--with-sample-data', action='store_true', 
                       help='Insertar datos de prueba')
    args = parser.parse_args()
    
    print("🚀 Iniciando proceso de inicialización de base de datos...")
    print("=" * 60)
    
    # Conectar a la base de datos
    if not connect_db():
        sys.exit(1)
    
    # Crear colecciones e índices
    if not create_collections():
        disconnect()
        sys.exit(1)
    
    # Insertar datos de prueba si se solicita
    if args.with_sample_data:
        if not insert_sample_data():
            disconnect()
            sys.exit(1)
    else:
        print("\n💡 Para insertar datos de prueba, ejecuta:")
        print("   python init_db.py --with-sample-data")
    
    # Desconectar
    disconnect()
    print("\n" + "=" * 60)
    print("✅ Proceso completado exitosamente")
    print("🎉 La base de datos está lista para usar")

if __name__ == '__main__':
    main()
