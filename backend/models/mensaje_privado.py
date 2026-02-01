from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime
from .usuario import Usuario

class MensajePrivado(Document):
    """
    Modelo de Mensaje Privado
    
    Representa un mensaje privado entre dos usuarios (similar a DM).
    
    Atributos:
        texto: Contenido del mensaje privado
        fechaDeCreado: Fecha y hora de creación
        emisor: Usuario que envía el mensaje
        receptor: Usuario que recibe el mensaje
    
    Relaciones:
        - 2 Usuarios (emisor y receptor)
    """
    
    # Campos básicos
    texto = StringField(required=True, max_length=1000)
    fechaDeCreado = DateTimeField(default=datetime.utcnow)
    
    # Relaciones (2 usuarios según el diagrama)
    emisor = ReferenceField(Usuario, required=True, reverse_delete_rule=2)  # CASCADE
    receptor = ReferenceField(Usuario, required=True, reverse_delete_rule=2)  # CASCADE
    
    # Estado del mensaje
    leido = DateTimeField(default=None)  # null si no ha sido leído
    
    # Metadata
    meta = {
        'collection': 'mensajes_privados',
        'db_alias': 'default',
        'indexes': [
            '-fechaDeCreado',  # Índice descendente para ordenar por fecha
            'emisor',
            'receptor',
            ('emisor', 'receptor'),  # Índice compuesto para búsquedas de conversaciones
            'leido'
        ]
    }
    
    def marcar_como_leido(self):
        """Marca el mensaje como leído"""
        if not self.leido:
            self.leido = datetime.utcnow()
            self.save()
    
    def to_dict(self):
        """Convierte el mensaje privado a diccionario"""
        return {
            'id': str(self.id),
            'texto': self.texto,
            'fechaDeCreado': self.fechaDeCreado.isoformat(),
            'emisor': self.emisor.to_dict() if self.emisor else None,
            'receptor': self.receptor.to_dict() if self.receptor else None,
            'leido': self.leido.isoformat() if self.leido else None
        }
    
    def __str__(self):
        return f"MensajePrivado(de={self.emisor.nickName if self.emisor else 'Unknown'}, " \
               f"para={self.receptor.nickName if self.receptor else 'Unknown'})"
