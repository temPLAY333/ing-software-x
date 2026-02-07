from models import Mensaje


def obtener_mis_mensajes(usuario, limit=50, offset=0):
    """
    Obtiene mensajes del usuario usando pymongo directamente para evitar problemas de thread local
    """
    try:
        autor_id = usuario.id if hasattr(usuario, 'id') else usuario
        
        # Usar pymongo directamente para evitar problemas de thread local
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        db = get_db('default')
        
        # Convertir autor_id a ObjectId si es necesario
        try:
            autor_oid = ObjectId(autor_id)
        except:
            autor_oid = autor_id
        
        # Buscar mensajes con pymongo
        mensajes_docs = list(
            db.mensajes.find({'autor': autor_oid})
            .sort('fechaDeCreado', -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convertir documentos a objetos Mensaje
        mensajes = []
        for doc in mensajes_docs:
            try:
                mensaje = Mensaje._from_son(doc)
                mensajes.append(mensaje)
            except Exception as e:
                print(f"⚠️ Error al convertir mensaje {doc.get('_id')}: {e}")
                continue
        
        # Contar total
        total = db.mensajes.count_documents({'autor': autor_oid})
        
        return mensajes, total
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error en obtener_mis_mensajes: {e}")
        return [], 0

