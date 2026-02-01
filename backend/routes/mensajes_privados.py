"""
Rutas para Mensajes Privados (CU0010)

Endpoints:
- POST /api/mensajes-privados - Crear mensaje privado
- GET /api/mensajes-privados/conversacion/<user_id> - Obtener conversación
- GET /api/mensajes-privados/conversaciones - Listar conversaciones
- PUT /api/mensajes-privados/<mensaje_id>/leer - Marcar como leído
- GET /api/mensajes-privados/no-leidos - Contar mensajes no leídos
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import Q
from datetime import datetime

from models import Usuario, MensajePrivado
from models.log import Log
from utils.validators import validar_mensaje_privado
from utils.decorators import rate_limit

# Crear blueprint
mensajes_privados_bp = Blueprint('mensajes_privados', __name__)


@mensajes_privados_bp.route('/mensajes-privados', methods=['POST'])
@jwt_required()
@rate_limit(max_requests=10, window_seconds=60)  # 10 mensajes por minuto
def crear_mensaje_privado():
    """
    Crear un nuevo mensaje privado
    
    Body:
        {
            "receptor_id": "user_id",
            "texto": "mensaje"
        }
    
    Returns:
        201: Mensaje creado exitosamente
        400: Datos inválidos
        404: Receptor no encontrado
        429: Rate limit excedido
    """
    try:
        # Obtener usuario autenticado (emisor)
        emisor_id = get_jwt_identity()
        emisor = Usuario.objects(id=emisor_id).first()
        
        if not emisor:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Obtener datos del request
        data = request.get_json()
        receptor_id = data.get('receptor_id')
        texto = data.get('texto', '').strip()
        
        # Validar datos
        es_valido, mensaje_error = validar_mensaje_privado(texto, emisor_id, receptor_id)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': mensaje_error,
                'code': 'VALIDATION_ERROR'
            }), 400
        
        # Buscar receptor
        receptor = Usuario.objects(id=receptor_id).first()
        if not receptor:
            return jsonify({
                'success': False,
                'error': 'Usuario receptor no encontrado',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        # Verificar que emisor != receptor
        if str(emisor.id) == str(receptor.id):
            return jsonify({
                'success': False,
                'error': 'No puedes enviarte mensajes a ti mismo',
                'code': 'SELF_MESSAGE_ERROR'
            }), 400
        
        # Crear mensaje privado
        mensaje = MensajePrivado(
            texto=texto,
            emisor=emisor,
            receptor=receptor
        )
        mensaje.save()
        
        # Registrar en logs
        Log.log_event(
            level='INFO',
            message=f'Mensaje privado enviado de {emisor.nickName} a {receptor.nickName}',
            user_id=str(emisor.id),
            action='send_private_message',
            ip_address=request.remote_addr,
            metadata={
                'mensaje_id': str(mensaje.id),
                'receptor_id': str(receptor.id),
                'texto_length': len(texto)
            }
        )
        
        # Retornar respuesta
        return jsonify({
            'success': True,
            'data': mensaje.to_dict()
        }), 201
        
    except Exception as e:
        # Log del error
        Log.log_event(
            level='ERROR',
            message=f'Error al crear mensaje privado: {str(e)}',
            user_id=emisor_id if 'emisor_id' in locals() else None,
            action='send_private_message_error',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/conversacion/<user_id>', methods=['GET'])
@jwt_required()
def obtener_conversacion(user_id):
    """
    Obtener conversación con un usuario específico
    
    Query params:
        limit: número de mensajes (default: 50)
        offset: offset para paginación (default: 0)
    
    Returns:
        200: Conversación obtenida
        404: Usuario no encontrado
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = Usuario.objects(id=usuario_actual_id).first()
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Verificar que el otro usuario existe
        otro_usuario = Usuario.objects(id=user_id).first()
        if not otro_usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        # Obtener parámetros de paginación
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Buscar conversación (mensajes entre ambos usuarios)
        mensajes = MensajePrivado.objects(
            Q(emisor=usuario_actual, receptor=otro_usuario) |
            Q(emisor=otro_usuario, receptor=usuario_actual)
        ).order_by('fechaDeCreado').skip(offset).limit(limit)
        
        # Contar total de mensajes
        total = MensajePrivado.objects(
            Q(emisor=usuario_actual, receptor=otro_usuario) |
            Q(emisor=otro_usuario, receptor=usuario_actual)
        ).count()
        
        # Marcar como leídos los mensajes recibidos
        mensajes_no_leidos = MensajePrivado.objects(
            emisor=otro_usuario,
            receptor=usuario_actual,
            leido=None
        )
        for msg in mensajes_no_leidos:
            msg.marcar_como_leido()
        
        return jsonify({
            'success': True,
            'data': {
                'conversacion': [mensaje.to_dict() for mensaje in mensajes],
                'total': total,
                'limit': limit,
                'offset': offset,
                'hasMore': (offset + limit) < total
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al obtener conversación',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/conversaciones', methods=['GET'])
@jwt_required()
def listar_conversaciones():
    """
    Listar todas las conversaciones del usuario actual
    
    Returns:
        200: Lista de conversaciones con último mensaje y contador de no leídos
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = Usuario.objects(id=usuario_actual_id).first()
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Obtener todos los mensajes donde el usuario participa
        mensajes = MensajePrivado.objects(
            Q(emisor=usuario_actual) | Q(receptor=usuario_actual)
        ).order_by('-fechaDeCreado')
        
        # Agrupar por conversación (usuario contrario)
        conversaciones_dict = {}
        
        for mensaje in mensajes:
            # Determinar el otro usuario
            if str(mensaje.emisor.id) == str(usuario_actual.id):
                otro_usuario = mensaje.receptor
            else:
                otro_usuario = mensaje.emisor
            
            otro_usuario_id = str(otro_usuario.id)
            
            # Si es la primera vez que vemos este usuario, agregarlo
            if otro_usuario_id not in conversaciones_dict:
                # Contar mensajes no leídos de este usuario
                no_leidos = MensajePrivado.objects(
                    emisor=otro_usuario,
                    receptor=usuario_actual,
                    leido=None
                ).count()
                
                conversaciones_dict[otro_usuario_id] = {
                    'usuario': otro_usuario.to_dict(),
                    'ultimoMensaje': mensaje.to_dict(),
                    'mensajesNoLeidos': no_leidos
                }
        
        # Convertir a lista
        conversaciones = list(conversaciones_dict.values())
        
        return jsonify({
            'success': True,
            'data': conversaciones
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al listar conversaciones',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/<mensaje_id>/leer', methods=['PUT'])
@jwt_required()
def marcar_como_leido(mensaje_id):
    """
    Marcar un mensaje como leído
    
    Returns:
        200: Mensaje marcado como leído
        404: Mensaje no encontrado
        403: No autorizado
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = Usuario.objects(id=usuario_actual_id).first()
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Buscar mensaje
        mensaje = MensajePrivado.objects(id=mensaje_id).first()
        if not mensaje:
            return jsonify({
                'success': False,
                'error': 'Mensaje no encontrado',
                'code': 'MESSAGE_NOT_FOUND'
            }), 404
        
        # Verificar que el usuario actual es el receptor
        if str(mensaje.receptor.id) != str(usuario_actual.id):
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para marcar este mensaje',
                'code': 'FORBIDDEN'
            }), 403
        
        # Marcar como leído
        mensaje.marcar_como_leido()
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(mensaje.id),
                'leido': mensaje.leido.isoformat() if mensaje.leido else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al marcar mensaje como leído',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/no-leidos', methods=['GET'])
@jwt_required()
def contar_no_leidos():
    """
    Contar mensajes no leídos del usuario actual
    
    Returns:
        200: Contador de mensajes no leídos
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = Usuario.objects(id=usuario_actual_id).first()
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Contar mensajes no leídos
        no_leidos = MensajePrivado.objects(
            receptor=usuario_actual,
            leido=None
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'noLeidos': no_leidos
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al contar mensajes no leídos',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/<mensaje_id>', methods=['DELETE'])
@jwt_required()
def eliminar_mensaje(mensaje_id):
    """
    Eliminar un mensaje privado (solo el emisor)
    
    Returns:
        200: Mensaje eliminado
        404: Mensaje no encontrado
        403: No autorizado
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = Usuario.objects(id=usuario_actual_id).first()
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Buscar mensaje
        mensaje = MensajePrivado.objects(id=mensaje_id).first()
        if not mensaje:
            return jsonify({
                'success': False,
                'error': 'Mensaje no encontrado',
                'code': 'MESSAGE_NOT_FOUND'
            }), 404
        
        # Verificar que el usuario actual es el emisor
        if str(mensaje.emisor.id) != str(usuario_actual.id):
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para eliminar este mensaje',
                'code': 'FORBIDDEN'
            }), 403
        
        # Eliminar mensaje
        mensaje.delete()
        
        # Log del evento
        Log.log_event(
            level='INFO',
            message=f'Mensaje privado eliminado por {usuario_actual.nickName}',
            user_id=str(usuario_actual.id),
            action='delete_private_message',
            ip_address=request.remote_addr,
            metadata={'mensaje_id': mensaje_id}
        )
        
        return jsonify({
            'success': True,
            'message': 'Mensaje eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al eliminar mensaje',
            'code': 'INTERNAL_ERROR'
        }), 500
