# camara_insights/app/infra/camara_api.py
import httpx
import asyncio

class CamaraAPI:
    def __init__(self, base_url: str = "https://dadosabertos.camara.leg.br/api/v2"):
        self.base_url = base_url

    async def get(self, endpoint: str, params: dict = None, retries: int = 3, backoff_factor: int = 60):
        """
        Método GET com lógica de retry para lidar com o erro 429 (Too Many Requests).
        """
        url = f"{self.base_url}{endpoint}"
        for attempt in range(retries):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(url, params=params, timeout=30.0)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    # Se o erro for 429, espera e tenta novamente
                    if e.response.status_code == 429:
                        wait_time = backoff_factor * (attempt + 1)
                        print(f"Erro 429 - Too Many Requests. Aguardando {wait_time} segundos para tentar novamente...")
                        await asyncio.sleep(wait_time)
                        continue # Próxima tentativa
                    else:
                        print(f"HTTP error occurred: {e}")
                        return None
                except httpx.RequestError as e:
                    print(f"An error occurred while requesting {e.request.url!r}.")
                    return None
        
        print(f"Falha ao obter dados de {url} após {retries} tentativas.")
        return None


camara_api_client = CamaraAPI()