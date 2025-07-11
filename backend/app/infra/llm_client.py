# app/infra/llm_client.py
import httpx
import json
from typing import Dict, Any

from app.core.settings import settings

class LLMClient:
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("A chave da API do OpenRouter não foi configurada. Defina a variável de ambiente OPENROUTER_API_KEY.")
        
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat-v3-0324:free"
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """Carrega o prompt do sistema a partir do arquivo de texto."""
        try:
            with open("prompts/analyze_proposition_prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise RuntimeError("Arquivo de prompt 'prompts/analyze_proposition_prompt.txt' não encontrado.")

    async def analyze_proposition(self, proposicao_id: int, ementa: str) -> Dict[str, Any]:
        """
        Envia a ementa de uma proposição para o LLM e retorna a análise estruturada.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        user_content = f"ID da Proposição: {proposicao_id}\nEmenta: {ementa}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"}
        }
        
        # Variável para armazenar a resposta para depuração
        llm_response_data = {}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    headers=headers, 
                    json=payload,
                    timeout=90.0
                )
                response.raise_for_status()
                
                llm_response_data = response.json()
                json_content_str = llm_response_data['choices'][0]['message']['content']
                
                return json.loads(json_content_str)

        except httpx.HTTPStatusError as e:
            print(f"Erro de HTTP ao chamar a API do LLM: {e.response.status_code} - {e.response.text}")

        except (json.JSONDecodeError, KeyError) as e:
            # --- Bloco de depuração melhorado ---
            print(f"--- ERRO DE PARSING JSON ---")
            print(f"Erro: {e}")
            raw_content = llm_response_data.get('choices', [{}])[0].get('message', {}).get('content', 'Nenhum conteúdo na resposta.')
            print(f"Conteúdo bruto recebido do LLM que causou o erro: '{raw_content}'")
            print(f"-----------------------------")
            # --- Fim do bloco de depuração ---

        except Exception as e:
            print(f"Um erro inesperado ocorreu no cliente LLM: {e}")
        
        return None

llm_client = LLMClient()