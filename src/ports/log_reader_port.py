"""
Port para lectura de logs.
Define la interfaz de entrada de datos de logs.
"""

from abc import ABC, abstractmethod


class LogReaderPort(ABC):
    """Interfaz para leer logs desde diferentes fuentes"""
    
    @abstractmethod
    def read_log(self, source: str) -> str:
        """
        Lee el contenido de un log.
        
        Args:
            source: Identificador de la fuente (path, URL, etc.)
        
        Returns:
            Contenido del log como string
        
        Raises:
            FileNotFoundError: Si la fuente no existe
            IOError: Si hay error de lectura
        """
        pass
