from services.seguidores_service import obtener_seguidores


class FakeUser:
    def __init__(self, seguidores=None):
        self.seguidores = seguidores or []


def test_obtener_seguidores():
    seguidores = [object(), object()]
    usuario = FakeUser(seguidores=seguidores)
    assert obtener_seguidores(usuario) == seguidores

