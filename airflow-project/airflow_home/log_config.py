from copy import deepcopy
from airflow.config_templates.airflow_local_settings import DEFAULT_LOGGING_CONFIG
import os
from airflow.utils.log.file_task_handler import FileTaskHandler
import colorama

import re
from typing import Any, Dict, Tuple

from airflow.models import TaskInstance

class ColorFileHandler(FileTaskHandler):
    """
    Advanced log handler that adds color based on log level and keywords.
    """

    def _read(self,
              ti: TaskInstance,
              try_number: int,
              metadata: Dict[str, Any] | None = None) -> Tuple[str, Dict[str, Any]]:
        
        colorama.init()
        log, metadata = super()._read(ti, try_number, metadata)
        processed_lines = []

        # Regular expression to match log level
        log_pattern = re.compile(r'\[(.*?)\]\s*\[(.*?)\]\s*(.*)')
        
        for line in log.splitlines():
            match = log_pattern.match(line)
            
            if match:
                timestamp, level, message = match.groups()
                colored_message = self._colorize_by_level(level, message)
                processed_lines.append(f'[{timestamp}] [{level}] {colored_message}')
            else:
                # Try to detect log level in the message itself
                if "ERROR" in line:
                    processed_lines.append(f'{colorama.Style.BRIGHT}{colorama.Fore.RED}{line}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}')
                elif "WARNING" in line:
                    processed_lines.append(f'{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}{line}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}')
                elif "INFO" in line:
                    processed_lines.append(f'{colorama.Fore.CYAN}{line}{colorama.Fore.RESET}')
                elif "SUCCESS" in line or "COMPLETED" in line:
                    processed_lines.append(f'{colorama.Style.BRIGHT}{colorama.Fore.GREEN}{line}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}')
                else:
                    processed_lines.append(f'{colorama.Style.BRIGHT}{colorama.Fore.RED}{line}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}')

        return "\n".join(processed_lines), metadata
    
    def _colorize_by_level(self, level: str, message: str) -> str:
        """Apply color formatting based on log level."""
        level = level.upper()
        
        if "ERROR" in level:
            return f'{colorama.Style.BRIGHT}{colorama.Fore.RED}{message}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}'
        elif "WARN" in level:
            return f'{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}{message}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}'
        elif "INFO" in level:
            return f'{colorama.Fore.CYAN}{message}{colorama.Fore.RESET}'
        elif "DEBUG" in level:
            return f'{colorama.Fore.BLUE}{message}{colorama.Fore.RESET}'
        elif "CRITICAL" in level:
            return f'{colorama.Style.BRIGHT}{colorama.Back.RED}{colorama.Fore.WHITE}{message}{colorama.Back.RESET}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}'
        else:
            return message
# class ColorFileHandler(FileTaskHandler):
#     ERROR_KEYWORDS = ["error", "exception"]

#     def _read(self, ti, try_number, metadata=None):
#         log, metadata = super()._read(ti, try_number, metadata)
#         processed_lines = []
#         for line in log.splitlines():
#             if any(keyword in line.lower() for keyword in self.ERROR_KEYWORDS):
#                 if line.startswith("["):
#                     timestamp, level, msg = line.split(maxsplit=2)
#                     processed_lines.append(
#                         f'{timestamp} {level} {colorama.Style.BRIGHT}{colorama.Fore.RED}{msg}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}'
#                     )
#                 else:
#                     processed_lines.append(
#                         f'{colorama.Style.BRIGHT}{colorama.Fore.RED}{line}{colorama.Fore.RESET}{colorama.Style.RESET_ALL}'
#                     )
#             else:
#                 processed_lines.append(line)
#         return "\n".join(processed_lines), metadata

LOGGING_CONFIG = deepcopy(DEFAULT_LOGGING_CONFIG)

LOGGING_CONFIG["handlers"]["color_handler"] = {
    'class': "log_config.ColorFileHandler",
    'formatter': 'airflow',
    'base_log_folder': os.path.join(os.path.expanduser('~/airflow'), 'logs'),
    'filters': ['mask_secrets']
}

LOGGING_CONFIG["loggers"]["airflow.task"]["handlers"] = ["task", "color_handler"]