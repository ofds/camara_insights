import logging

# app/core/rate_limiter.py
import asyncio
import time
from collections import deque

class RateLimiter:
    """
    Uma classe para controlar a taxa de requisições e não exceder
    um limite em uma janela de tempo específica.
    """
    def __init__(self, requests_per_minute: int):
        self.rate_limit = requests_per_minute
        self.time_window = 60  # em segundos
        self.request_timestamps = deque()

    async def acquire(self):
        """
        Aguarda o tempo necessário para garantir que a próxima requisição
        respeite o limite de taxa.
        """
        while len(self.request_timestamps) >= self.rate_limit:
            # Tempo da requisição mais antiga na janela
            oldest_request_time = self.request_timestamps[0]
            
            # Tempo decorrido desde a requisição mais antiga
            elapsed_time = time.time() - oldest_request_time
            
            if elapsed_time < self.time_window:
                # Se a janela de tempo ainda não passou, calcula o tempo a esperar
                time_to_wait = self.time_window - elapsed_time
                logging.info(f"--- [RATE LIMITER] Limite atingido. Aguardando {time_to_wait:.2f} segundos... ---")
                await asyncio.sleep(time_to_wait)
            
            # Remove o timestamp da requisição mais antiga da fila
            self.request_timestamps.popleft()
        
        # Adiciona o timestamp da nova requisição
        self.request_timestamps.append(time.time())