# procurar a pasta documents na maquina do usuario
import os

def find_documents_folder():
    home = os.path.expanduser("~")
    documents = os.path.join(home, "Documents")
    # Define o caminho para a pasta ChromaGithub dentro da pasta Documents
    chroma_folder = os.path.join(documents, "ChromaGithub")
    
    # Cria a pasta Documents se ela não existir
    if not os.path.exists(documents):
        os.makedirs(documents)
    
    # Cria a pasta ChromaGithub se ela não existir
    if not os.path.exists(chroma_folder):
        os.makedirs(chroma_folder)
        
    return chroma_folder

# retornar o caminho universal para a pasta "ChromaGithub" 
def locate_university_folder():
    home = os.path.expanduser("~")
    documents = os.path.join(home, "Documents")
    if not os.path.exists(documents):
        return None

    # procura por nomes que contenham tanto "chroma"
    for root, dirs, _ in os.walk(documents):
        for d in dirs:
            name = d.lower()
            if name == "chromagithub":   
                return os.path.join(root, d)
    return None


# testar a funcao
if __name__ == "__main__":
    #folder = find_documents_folder()
    #print("Caminho da pasta ChromaGithub:", folder)
    universal_folder = locate_university_folder()
    print("Caminho universal da pasta ChromaGithub:", universal_folder)