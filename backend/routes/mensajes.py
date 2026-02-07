"""
Rutas para mensajes públicos (mensajes propios)

Endpoints:
- GET /api/mensajes/mios - Obtener mensajes propios
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Usuario
from services.mensajes_service import obtener_mis_mensajes

mensajes_bp = Blueprint("mensajes", __name__)


@mensajes_bp.route("/mensajes/mios", methods=["GET"])
@jwt_required()
def obtener_mis_mensajes_route():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.objects(id=usuario_id).first()

        if not usuario:
            return jsonify({
                "success": False,
                "error": "Usuario no autenticado",
                "code": "AUTH_ERROR",
            }), 401

        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

        mensajes, total = obtener_mis_mensajes(usuario, limit, offset)

        return jsonify({
            "success": True,
            "data": {
                "mensajes": [mensaje.to_dict() for mensaje in mensajes],
                "total": total,
                "limit": limit,
                "offset": offset,
                "hasMore": (offset + limit) < total,
            }
        }), 200
    except Exception:
        return jsonify({
            "success": False,
            "error": "Error al obtener mensajes propios",
            "code": "INTERNAL_ERROR",
        }), 500

