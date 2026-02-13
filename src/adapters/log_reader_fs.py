"""
Adapter de lectura de logs desde filesystem.
Implementa LogReaderPort para leer archivos locales.
"""

import logging
from pathlib import Path

from ..ports.log_reader_port import LogReaderPort
from ..config.constants import Constants


logger = logging.getLogger(__name__)


class FileSystemLogReader(LogReaderPort):
    """Lee logs desde archivos del sistema de archivos local"""
    
    def read_log(self, source: str) -> str:
        """
        Lee un archivo de logs del filesystem.
        
        Args:
            source: Path al archivo de logs
        
        Returns:
            Contenido del archivo como string
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            IOError: Si hay error de lectura
        """
        path = Path(source)
        
        if not path.exists():
            logger.error(f"{Constants.ERROR_FILE_NOT_FOUND}: {source}")
            raise FileNotFoundError(f"Archivo no encontrado: {source}")
        
        if not path.is_file():
            logger.error(f"La ruta no es un archivo: {source}")
            raise ValueError(f"La ruta no es un archivo: {source}")
        
        logger.debug(f"Leyendo archivo: {source}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.debug(f"Archivo leído: {len(content)} caracteres")
            return content
            
        except Exception as e:
            logger.error(f"Error al leer archivo {source}: {e}")
            raise IOError(f"Error al leer archivo: {e}") from e
