from models import Mensaje


def obtener_mis_mensajes(usuario, limit=50, offset=0):
    mensajes = (
        Mensaje.objects(autor=usuario)
        .order_by("-fechaDeCreado")
        .skip(offset)
        .limit(limit)
    )

    total = Mensaje.objects(autor=usuario).count()
    return mensajes, total

