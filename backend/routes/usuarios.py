"""
Rutas para perfil de usuario y subida de fotos

- POST /api/upload/avatar - Subir foto de perfil (devuelve URL)
- PATCH /api/usuarios/me - Actualizar perfil (fotoUsuario, fotoUsuarioPortada, biografia)
"""

import os
import uuid
from bson import ObjectId
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.connection import get_db

import utils.mongo_helpers

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB

usuarios_bp = Blueprint('usuarios', __name__)


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_folder():
    return current_app.config['UPLOAD_AVATARS_FOLDER']


@usuarios_bp.route('/upload/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """
    Sube una imagen como avatar. Guarda el archivo en el servidor y devuelve la URL pública.
    La URL se puede guardar en el perfil con PATCH /api/usuarios/me.

    Form-data: 'file' (imagen PNG, JPEG, GIF o WebP; máx 5 MB)

    Returns:
        200: { "success": true, "url": "http://..." }
        400: sin archivo o tipo no permitido
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No se envió ningún archivo',
            'code': 'NO_FILE'
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Nombre de archivo vacío',
            'code': 'NO_FILE'
        }), 400

    if not _allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'Formato no permitido. Use: {", ".join(ALLOWED_EXTENSIONS)}',
            'code': 'INVALID_TYPE'
        }), 400

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_AVATAR_SIZE:
        return jsonify({
            'success': False,
            'error': 'El archivo supera el tamaño máximo (5 MB)',
            'code': 'FILE_TOO_BIG'
        }), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    folder = _upload_folder()
    path = os.path.join(folder, safe_name)
    file.save(path)

    # URL que el frontend puede usar en <img src="..."> y guardar en fotoUsuario
    base_url = request.host_url.rstrip('/')
    url = f"{base_url}/uploads/avatars/{safe_name}"

    return jsonify({
        'success': True,
        'url': url
    }), 200


@usuarios_bp.route('/usuarios/me', methods=['PATCH'])
@jwt_required()
def update_me():
    """
    Actualiza el perfil del usuario autenticado.
    Body: { "fotoUsuario": "url?", "fotoUsuarioPortada": "url?", "biografia": "texto?" }

    Returns:
        200: perfil actualizado
        401: no autenticado
    """
    user_id = get_jwt_identity()
    usuario = utils.mongo_helpers.get_usuario_by_id(user_id)
    if not usuario:
        return jsonify({
            'success': False,
            'error': 'Usuario no encontrado',
            'code': 'USER_NOT_FOUND'
        }), 401

    data = request.get_json() or {}
    updates = {}
    if 'fotoUsuario' in data:
        updates['fotoUsuario'] = (data['fotoUsuario'] or '').strip()
    if 'fotoUsuarioPortada' in data:
        updates['fotoUsuarioPortada'] = (data['fotoUsuarioPortada'] or '').strip()
    if 'biografia' in data:
        updates['biografia'] = (data['biografia'] or '')[:500]

    if not updates:
        return jsonify({'success': True, 'data': usuario.to_dict()}), 200

    try:
        oid = ObjectId(user_id)
    except Exception:
        return jsonify({'success': False, 'error': 'ID de usuario inválido', 'code': 'INVALID_ID'}), 400

    db = get_db('default')
    result = db.usuarios.update_one({'_id': oid}, {'$set': updates})
    if result.matched_count == 0:
        return jsonify({'success': False, 'error': 'Usuario no encontrado', 'code': 'USER_NOT_FOUND'}), 404

    usuario_actualizado = utils.mongo_helpers.get_usuario_by_id(user_id)
    return jsonify({
        'success': True,
        'data': usuario_actualizado.to_dict()
    }), 200
