class FakeUsuario:
    def __init__(self, user_id):
        self.id = user_id


class FakeMensaje:
    def to_dict(self):
        return {
            "id": "msg_1",
            "texto": "hola",
            "fechaDeCreado": "2026-01-01T10:00:00Z"
        }


class FakeQuery:
    def __init__(self, usuario):
        self._usuario = usuario

    def select_related(self, *args):
        return self

    def first(self):
        return self._usuario


def test_obtener_mensajes_mios(app_client, auth_headers, monkeypatch):
    import models
    import routes.mensajes as mensajes_route
    import utils.mongo_helpers

    usuario = FakeUsuario("user_1")

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_obtener_mis_mensajes(user, limit, offset):
        return [FakeMensaje()], 1

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "obtener_mis_mensajes", fake_obtener_mis_mensajes)

    response = app_client.get("/api/mensajes/mios", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["mensajes"][0]["id"] == "msg_1"


def test_obtener_mensajes_mios_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.get("/api/mensajes/mios")
    assert response.status_code == 401


def test_obtener_mensajes_mios_usuario_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el usuario no existe"""
    import utils.mongo_helpers

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/mensajes/mios", headers=auth_headers)
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["success"] is False
    assert "no autenticado" in payload["error"].lower() or "no encontrado" in payload["error"].lower()


def test_obtener_mensajes_mios_con_paginacion(app_client, auth_headers, monkeypatch):
    """Test que verifica la paginación de mensajes"""
    import models
    import routes.mensajes as mensajes_route
    import utils.mongo_helpers

    usuario = FakeUsuario("user_1")

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_obtener_mis_mensajes(user, limit, offset):
        mensajes = [FakeMensaje() for _ in range(limit)]
        return mensajes, 50  # Total de 50 mensajes

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "obtener_mis_mensajes", fake_obtener_mis_mensajes)

    response = app_client.get("/api/mensajes/mios?limit=10&offset=0", headers=auth_headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["limit"] == 10
    assert payload["data"]["offset"] == 0
    assert payload["data"]["total"] == 50
    assert payload["data"]["hasMore"] is True

