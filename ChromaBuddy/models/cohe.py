# -*- coding: utf-8 -*-
import cohere

def generate(api_key: str, system_prompt: str, user_prompt: str) -> str:
    try:
        # Inicializar cliente
        co = cohere.ClientV2(api_key)

        # Criar lista de mensagens
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Fazer a requisição usando o método chat
        resposta = co.chat(
            model="command-a-03-2025",
            messages=messages
        )

        return resposta.message.content[0].text

    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

# Exemplo de uso
if __name__ == "__main__":
    # Substitua pela sua chave da API
    api_key = "lXInEtdWZndCJb2a44x3CNo0c8twHlW5GFD5wnQZ"
    system = "Você é um assistente útil para desenvolvimento de software."
    user = "Como posso melhorar meu código Python?"

    resposta = generate(api_key, system, user)
    print(resposta)
