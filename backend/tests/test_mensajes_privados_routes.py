from datetime import datetime


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        self.id = user_id
        self.nickName = nick
        self.nombre = "Nombre"
        self.apellido = "Apellido"
        self.fotoUsuario = ""

    def to_dict(self):
        return {
            "id": str(self.id),
            "nickName": self.nickName,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "fotoUsuario": self.fotoUsuario,
        }


class FakeMensajePrivado:
    def __init__(self, texto, emisor, receptor):
        self.id = "msg_1"
        self.texto = texto
        self.emisor = emisor
        self.receptor = receptor
        self.leido = None
        self.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)

    def marcar_como_leido(self):
        self.leido = datetime(2026, 1, 1, 10, 5, 0)

    def save(self):
        return self

    def to_dict(self):
        return {
            "id": str(self.id),
            "texto": self.texto,
            "fechaDeCreado": self.fechaDeCreado.isoformat(),
            "emisor": self.emisor.to_dict(),
            "receptor": self.receptor.to_dict(),
            "leido": self.leido.isoformat() if self.leido else None,
        }


class FakeQuerySet:
    def __init__(self, data, count_value=None):
        self._data = list(data)
        self._count = count_value if count_value is not None else len(self._data)

    def order_by(self, *_args, **_kwargs):
        return self

    def skip(self, value):
        self._data = self._data[value:]
        return self

    def limit(self, value):
        self._data = self._data[:value]
        return self

    def count(self):
        return self._count

    def first(self):
        return self._data[0] if self._data else None

    def __iter__(self):
        return iter(self._data)


def test_listar_conversaciones(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados

    usuario_actual = FakeUsuario("user_1", "juan")
    otro_usuario = FakeUsuario("user_2", "maria")
    mensaje = FakeMensajePrivado("hola", usuario_actual, otro_usuario)

    def fake_usuario_objects(**kwargs):
        if kwargs.get("id") == "user_1":
            return FakeQuerySet([usuario_actual])
        return FakeQuerySet([])

    def fake_mensaje_objects(**kwargs):
        if "leido" in kwargs:
            return FakeQuerySet([], count_value=0)
        return FakeQuerySet([mensaje])

    monkeypatch.setattr(mensajes_privados.Usuario, "objects", staticmethod(fake_usuario_objects))
    monkeypatch.setattr(mensajes_privados.MensajePrivado, "objects", staticmethod(fake_mensaje_objects))

    response = app_client.get("/api/mensajes-privados/conversaciones", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"][0]["usuario"]["id"] == "user_2"


def test_obtener_conversacion(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados

    usuario_actual = FakeUsuario("user_1", "juan")
    otro_usuario = FakeUsuario("user_2", "maria")
    mensaje = FakeMensajePrivado("hola", usuario_actual, otro_usuario)
    no_leido = FakeMensajePrivado("hola", otro_usuario, usuario_actual)

    def fake_usuario_objects(**kwargs):
        if kwargs.get("id") == "user_1":
            return FakeQuerySet([usuario_actual])
        if kwargs.get("id") == "user_2":
            return FakeQuerySet([otro_usuario])
        return FakeQuerySet([])

    def fake_mensaje_objects(**kwargs):
        if "leido" in kwargs:
            return FakeQuerySet([no_leido])
        return FakeQuerySet([mensaje], count_value=1)

    monkeypatch.setattr(mensajes_privados.Usuario, "objects", staticmethod(fake_usuario_objects))
    monkeypatch.setattr(mensajes_privados.MensajePrivado, "objects", staticmethod(fake_mensaje_objects))

    response = app_client.get("/api/mensajes-privados/conversacion/user_2", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["conversacion"][0]["texto"] == "hola"


def test_crear_mensaje_privado(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados

    usuario_actual = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")

    def fake_usuario_objects(**kwargs):
        if kwargs.get("id") == "user_1":
            return FakeQuerySet([usuario_actual])
        if kwargs.get("id") == "user_2":
            return FakeQuerySet([receptor])
        return FakeQuerySet([])

    monkeypatch.setattr(mensajes_privados.Usuario, "objects", staticmethod(fake_usuario_objects))
    monkeypatch.setattr(mensajes_privados, "MensajePrivado", FakeMensajePrivado)
    monkeypatch.setattr(mensajes_privados, "validar_mensaje_privado", lambda *args: (True, ""))
    monkeypatch.setattr(mensajes_privados.Log, "log_event", lambda **_kwargs: None)

    response = app_client.post(
        "/api/mensajes-privados",
        json={"receptor_id": "user_2", "texto": "hola"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["texto"] == "hola"


def test_crear_mensaje_privado_invalido(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados

    usuario_actual = FakeUsuario("user_1", "juan")

    def fake_usuario_objects(**kwargs):
        if kwargs.get("id") == "user_1":
            return FakeQuerySet([usuario_actual])
        return FakeQuerySet([])

    monkeypatch.setattr(mensajes_privados.Usuario, "objects", staticmethod(fake_usuario_objects))
    monkeypatch.setattr(mensajes_privados, "validar_mensaje_privado", lambda *args: (False, "error"))

    response = app_client.post(
        "/api/mensajes-privados",
        json={"receptor_id": "user_2", "texto": ""},
        headers=auth_headers,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False

