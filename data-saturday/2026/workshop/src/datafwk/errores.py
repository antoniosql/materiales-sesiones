class ErrorFramework(Exception):
    """Error base del framework."""


class ConfiguracionInvalida(ErrorFramework):
    """La configuración (entorno, fuentes o contrato) no es válida."""


class ContratoIncumplido(ErrorFramework):
    """Los datos no cumplen el contrato y la política es 'fallar'."""
