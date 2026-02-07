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

    def first(self):
        return self._usuario


def test_obtener_mensajes_mios(app_client, auth_headers, monkeypatch):
    import models
    import routes.mensajes as mensajes_route

    usuario = FakeUsuario("user_1")

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    def fake_obtener_mis_mensajes(user, limit, offset):
        return [FakeMensaje()], 1

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(mensajes_route, "obtener_mis_mensajes", fake_obtener_mis_mensajes)

    response = app_client.get("/api/mensajes/mios", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["mensajes"][0]["id"] == "msg_1"

