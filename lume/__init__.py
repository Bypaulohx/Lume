"""
Lume V2.0 - Ferramenta Profissional de Análise de Segurança Web
Do latim: iluminar falhas escondidas
"""

__version__ = "2.0.0"
__author__ = "Lume Security Team"
__description__ = "Advanced web vulnerability scanner with behavioral and infrastructure analysis"

from .core.logger import setup_logger
from .core.config import Config

__all__ = ["setup_logger", "Config", "__version__"]
