"""Feedback 'inteligente': convierte errores técnicos en pistas comprensibles para 4º ESO."""

ERROR_HINTS = {
    "SyntaxError": "Python no entiende alguna línea. Revisa que las instrucciones if/for/while/def terminen en ':' "
                   "y que paréntesis y comillas estén cerrados.",
    "IndentationError": "Problema de sangría. El código dentro de un if, for, while o def debe ir desplazado "
                        "4 espacios, y todas las líneas del mismo bloque igual de desplazadas.",
    "TabError": "Mezclas tabuladores y espacios. Usa solo espacios (4 por nivel).",
    "NameError": "Usas un nombre que no existe. Comprueba mayúsculas/minúsculas (Pin no es pin), "
                 "que la variable esté creada antes de usarla y que hayas hecho el import necesario.",
    "TypeError": "Mezclas tipos que no encajan (por ejemplo, sumar texto y número) o llamas a una función "
                 "con un número equivocado de parámetros.",
    "ZeroDivisionError": "Divides entre cero. Piensa qué pasa si la lista está vacía o si mínimo y máximo son iguales.",
    "IndexError": "Accedes a una posición de la lista que no existe. Recuerda que la primera es la 0 y la última len(lista)-1.",
    "KeyError": "Buscas en un diccionario una clave que no existe. Revisa cómo está escrita.",
    "AttributeError": "Llamas a un método que ese objeto no tiene. Revisa el nombre (read_u16, toggle, value…).",
    "ValueError": "Un valor tiene el tipo correcto pero un contenido no válido (por ejemplo int('hola')).",
    "ImportError": "Ese módulo no está disponible aquí. Usa los de MicroPython: machine, time, network, neopixel, bluetooth…",
    "ModuleNotFoundError": "Ese módulo no está disponible aquí. Usa los de MicroPython: machine, time, network, neopixel, bluetooth…",
    "SecurityError": "Has usado algo que no está permitido en los ejercicios evaluados.",
    "Timeout": "Tu programa no termina: probablemente hay un bucle infinito (while True). En los ejercicios "
               "evaluados usa un for con un número fijo de repeticiones o una condición que llegue a cumplirse.",
    "TimeoutError": "Tu programa no termina: probablemente hay un bucle infinito (while True). Usa un for con "
                    "un número fijo de repeticiones.",
    "RecursionError": "Una función se llama a sí misma sin parar.",
    "MemoryError": "Tu programa usa demasiada memoria. ¡En un microcontrolador la RAM es muy limitada!",
    "TooLong": "El código es demasiado largo para este ejercicio.",
    "Crash": "El programa se detuvo de forma inesperada. Revisa que no haya bucles enormes.",
}


def explain_error(err: dict, item_hints: dict | None = None) -> str:
    kind = err.get("type", "")
    hints = item_hints or {}
    base = hints.get(kind) or ERROR_HINTS.get(kind, "Se ha producido un error al ejecutar tu código.")
    where = f" (línea {err['line']})" if err.get("line") else ""
    msg = err.get("message", "")
    return f"{kind}{where}: {msg}\n💡 {base}" if msg else f"{kind}{where}\n💡 {base}"


def summary_message(score: float, passing: float, passed: bool) -> str:
    pct = int(score * 100 + 0.5)
    need = int(passing * 100 + 0.5)
    if passed and pct == 100:
        return f"¡Perfecto! {pct}%. Sección superada. 🚀"
    if passed:
        return f"¡Superada con un {pct}%! (mínimo {need}%). Revisa los fallos para aprender de ellos."
    if pct >= need - 15:
        return f"Casi: {pct}% (necesitas {need}%). Lee las pistas y vuelve a intentarlo."
    return f"{pct}% (necesitas {need}%). Repasa la teoría y los ejemplos de esta sección antes de reintentar."
