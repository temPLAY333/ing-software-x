"""
Rutas para seguidores del usuario

Endpoints:
- GET /api/usuarios/seguidores - Obtener seguidores del usuario actual
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Usuario
from services.seguidores_service import obtener_seguidores

seguidores_bp = Blueprint("seguidores", __name__)


@seguidores_bp.route("/usuarios/seguidores", methods=["GET"])
@jwt_required()
def listar_seguidores():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.objects(id=usuario_id).first()

        if not usuario:
            return jsonify({
                "success": False,
                "error": "Usuario no autenticado",
                "code": "AUTH_ERROR",
            }), 401

        seguidores = obtener_seguidores(usuario)

        return jsonify({
            "success": True,
            "data": [seguidor.to_dict() for seguidor in seguidores],
        }), 200
    except Exception:
        return jsonify({
            "success": False,
            "error": "Error al obtener seguidores",
            "code": "INTERNAL_ERROR",
        }), 500

