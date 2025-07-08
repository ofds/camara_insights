# app/infra/camara_api.py
import httpx

class CamaraAPI:
    def __init__(self, base_url: str = "https://dadosabertos.camara.leg.br/api/v2"):
        self.base_url = base_url

    async def get(self, endpoint: str, params: dict = None):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}{endpoint}", params=params)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
                return None
            except httpx.RequestError as e:
                print(f"An error occurred while requesting {e.request.url!r}.")
                return None

camara_api_client = CamaraAPI()