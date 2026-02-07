class FakeUsuario:
    def __init__(self, user_id, seguidores=None):
        self.id = user_id
        self.seguidores = seguidores or []

    def to_dict(self):
        return {
            "id": str(self.id),
            "nickName": "user",
            "nombre": "User",
            "apellido": "Test"
        }


class FakeQuery:
    def __init__(self, usuario):
        self._usuario = usuario

    def first(self):
        return self._usuario


def test_listar_seguidores_ok(app_client, auth_headers, monkeypatch):
    import models

    seguidor = FakeUsuario("seg_1")
    usuario = FakeUsuario("user_1", seguidores=[seguidor])

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))

    response = app_client.get("/api/usuarios/seguidores", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert len(payload["data"]) == 1


def test_listar_seguidores_vacio(app_client, auth_headers, monkeypatch):
    import models

    usuario = FakeUsuario("user_1", seguidores=[])

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))

    response = app_client.get("/api/usuarios/seguidores", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"] == []
    assert payload["code"] == "NO_FOLLOWERS"

