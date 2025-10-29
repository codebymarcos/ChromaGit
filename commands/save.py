# save => push

# importar modulos
import os
import sys
import shutil

__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
sys.path.append(__path__)
from cli.collor import red_bold, green_bold, yellow
from utils.config import locate_university_folder, find_documents_folder
from cli.progress import ProgressLogger

class Save:
    def __init__(self):
        # procurar a pasta .hub_<nome do repositorio> no workspace atual
        self.path = os.getcwd()
        self.invisible_folder = None

    def locate_invisible_folder(self):
        if not self.path:
            print(red_bold("[ERRO] Diretório de trabalho não encontrado"))
            return None
            
        current_folder = os.path.basename(self.path)
        invisible_folder = os.path.join(self.path, f".hub_{current_folder}")
        return invisible_folder

    # procurar a pasta chromagithub na pasta documents
    def locate_hub_folder(self):
        documents_folder = find_documents_folder()
        if not documents_folder:
            print(red_bold("[ERRO] Pasta Documents não encontrada"))
            return None
        
        # find_documents_folder() já retorna o caminho da pasta ChromaGithub
        hub_folder = documents_folder
        return hub_folder

    def save(self):
        # localizar pastas necessárias
        invisible_folder = self.locate_invisible_folder()
        if not invisible_folder or not os.path.exists(invisible_folder):
            print(red_bold("[ERRO] Repositório não inicializado"))
            print(red_bold("[INFO] Execute: chromagit init"))
            return False
        
        hub_folder = self.locate_hub_folder()
        if not hub_folder:
            return False
        
        # destino: pasta com nome do repositório dentro de ChromaGithub
        repo_name = os.path.basename(self.path)
        destination = os.path.join(hub_folder, repo_name)
        
        try:
            # prepara destino (limpa se existir, cria se não)
            if os.path.exists(destination):
                for item in os.listdir(destination):
                    target_path = os.path.join(destination, item)
                    try:
                        if os.path.isdir(target_path):
                            shutil.rmtree(target_path)
                        else:
                            os.remove(target_path)
                    except PermissionError:
                        print(yellow(f"[AVISO] Permissão negada: {item}"))
            else:
                os.makedirs(destination, exist_ok=True)
            
            # lista itens a copiar
            items = os.listdir(invisible_folder)
            # copia o conteúdo da pasta invisível para o destino com barra de progresso
            with ProgressLogger("Salvando no ChromaGithub...", total=len(items)) as p:
                for item in items:
                    src_path = os.path.join(invisible_folder, item)
                    dst_path = os.path.join(destination, item)
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dst_path)
                    p.update(1, custom_message=item)
            
            print(green_bold("[OK] Alterações salvas em ChromaGithub"))
            print(yellow("Destino: ") + destination)
            return True
        except Exception as e:
            print(red_bold(f"[ERRO] {str(e)}"))
            return False

if __name__ == "__main__":
    saver = Save()
    success = saver.save()
    sys.exit(0 if success else 1)