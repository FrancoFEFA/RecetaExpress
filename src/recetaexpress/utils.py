"""Utilidades compartidas del paquete."""

from unidecode import unidecode


def safe_filename(nombre: str) -> str:
    """Normaliza un nombre a ASCII y lo vuelve seguro para nombres de archivo.

    Sin acentos, sin espacios ni caracteres especiales, en minúsculas.
    """
    return "".join(c if c.isalnum() else "_" for c in unidecode(nombre)).lower()
