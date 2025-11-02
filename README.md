# ChromaGit

**ChromaGit**: Um sistema de versionamento local inspirado no Git, mas feito para ser rapido, adaptavel e simples. Como um camaleao, ele se adapta as suas necessidades!

## O que e isso?

Imagine o Git, mas sem precisar de um servidor remoto. O ChromaGit salva tudo localmente na sua pasta `Documents/ChromaGithub`. Perfeito para projetos pessoais, prototipos ou quando voce quer controle total dos seus arquivos.

## Funcionalidades principais

- **Init**: Inicializa um repositorio ChromaGit no diretorio atual
- **New**: Cria um novo repositorio vazio em `Documents/ChromaGithub`
- **Hub**: Explore e gerencie todos os seus repositorios com um menu interativo
  - Visualize a estrutura de pastas como uma arvore bonita
  - Escaneie todo o conteudo e gere documentacao automatica
  - Edite arquivos diretamente no terminal com destaque de sintaxe
- **Duple**: Copia um repositorio do `ChromaGithub` para o seu workspace
- **Commit**: Salva mudancas em uma area invisivel com mensagem
- **Save**: Copia o repositorio de volta para `Documents/ChromaGithub`

## Como instalar

1. **Clone o repositorio:**
   ```bash
   git clone https://github.com/codebymarcos/ChromaGit.git
   cd ChromaGit
   ```

2. **Crie um ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependencias:**
   ```bash
   pip install prompt_toolkit pygments
   ```

4. **Execute:**
   ```bash
   python main.py
   ```

## Como usar

Apos executar `python main.py`, voce vera um prompt como:
```
chromagit > nome_da_pasta $
```

### Comandos basicos:

- `init` - Inicializar repositorio no diretorio atual
- `new` - Criar novo repositorio vazio
- `hub` - Abrir o gerenciador de repositorios
- `duple nome_repo` - Copiar repositorio para workspace
- `commit -m "sua mensagem"` - Salvar mudancas
- `save` - Enviar para ChromaGithub
- `help` - Ver todos os comandos
- `exit` - Sair

### Exemplo de workflow:

1. `new` -> Cria "meu_projeto"
2. `duple meu_projeto` -> Copia para workspace
3. Edite seus arquivos normalmente
4. `commit -m "primeira versao"` -> Salva localmente
5. `save` -> Envia para ChromaGithub

## Por que ChromaGit?

- **Local**: Tudo fica no seu computador
- **Simples**: Interface em portugues, comandos intuitivos
- **Flexivel**: Adapta-se ao seu jeito de trabalhar
- **Rapido**: Sem sincronizacao com servidores
- **Visual**: Ferramentas integradas para explorar codigo

## Arquitetura

- `main.py` - CLI principal
- `commands/` - Modulos dos comandos
- `cli/` - Utilitarios de interface
- `utils/` - Funcoes auxiliares
- `commands/noctis_map/` - Ferramentas de visualizacao e edicao

## Contribuicao

Sinta-se a vontade para abrir issues, sugerir melhorias ou enviar pull requests!

---

**Feito com ❤️ por codebymarcos**
