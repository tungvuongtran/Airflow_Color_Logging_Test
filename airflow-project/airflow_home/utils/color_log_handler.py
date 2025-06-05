import os
import re
from typing import Any, Dict, Tuple

import colorama
from airflow.utils.log.file_task_handler import FileTaskHandler
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
                    processed_lines.append(line)

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