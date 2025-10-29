# sistema de log de progresso em tempo real
import sys
import time
from datetime import datetime

# importar cores
import os
__path__ = os.path.abspath(os.path.dirname(__file__) + '/..')
if __path__ not in sys.path:
    sys.path.append(__path__)
from cli.collor import yellow, green_bold, red_bold

class ProgressLogger:
    # Log de progresso em tempo real com barra visual
    
    def __init__(self, message, total=100, show_percentage=True, show_time=True):
        self.message = message
        self.total = total
        self.current = 0
        self.show_percentage = show_percentage
        self.show_time = show_time
        self.start_time = None
        self.last_update_time = None
        
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()
        return False
    
    def start(self):
        # iniciar o log de progresso
        self.start_time = time.time()
        self.last_update_time = self.start_time
        sys.stdout.write(f"\n{yellow('chromagit >')} {self.message}\n")
        sys.stdout.flush()
    
    def update(self, increment=1, custom_message=None):
        # atualizar o progresso
        self.current = min(self.current + increment, self.total)
        self.last_update_time = time.time()
        self._display(custom_message)
    
    def _display(self, custom_message=None):
        # exibir o progresso atual
        # Calcula porcentagem
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        
        # Calcula tempo decorrido
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Calcula tempo estimado restante
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            remaining_str = self._format_time(remaining)
        else:
            remaining_str = "calculando..."
        
        # Barra de progresso visual (20 caracteres)
        bar_width = 20
        filled = int(bar_width * self.current / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        
        # Monta a mensagem
        parts = [f"[{bar}]"]
        
        if self.show_percentage:
            parts.append(f"{percentage:.1f}%")
        
        if self.show_time:
            elapsed_str = self._format_time(elapsed)
            parts.append(f"({elapsed_str} / {remaining_str})")
        
        progress_line = " ".join(parts)
        
        # Mensagem customizada ou padrão
        message = custom_message if custom_message else f"{self.current}/{self.total}"
        
        # Move cursor para o início da linha e sobrescreve
        sys.stdout.write(f"\r{yellow('chromagit >')} {self.message} {progress_line} | {message}")
        sys.stdout.flush()
    
    def _format_time(self, seconds):
        # formatar tempo em string legível
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"
    
    def finish(self, success_message=None):
        # finalizar o log de progresso
        # Garante que chegou a 100%
        if self.current < self.total:
            self.current = self.total
            self._display()
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_str = self._format_time(elapsed)
        
        # Limpa a linha de progresso e mostra resultado final
        sys.stdout.write("\r" + " " * 100 + "\r")  # Limpa a linha
        
        if success_message:
            print(f"{green_bold('[OK]')} {success_message} ({elapsed_str})")
        else:
            print(f"{green_bold('[OK]')} {self.message} concluído ({elapsed_str})")


class SimpleProgress:
    # Progresso simples sem barra visual
    
    def __init__(self, initial_message=None):
        self.start_time = time.time()
        if initial_message:
            print(f"{yellow('chromagit >')} {initial_message}")
    
    def step(self, message):
        # exibir um passo do progresso
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        print(f"  {yellow('→')} {message} ({elapsed_str})")
    
    def done(self, message="Concluído"):
        # finalizar o progresso
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        print(f"{green_bold('[OK]')} {message} ({elapsed_str})")
    
    def error(self, message):
        # exibir um erro
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)
        print(f"{red_bold('[ERRO]')} {message} ({elapsed_str})")
    
    def _format_time(self, seconds):
        # formatar tempo em string legível
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"


# Testes
if __name__ == "__main__":
    print("Teste 1: ProgressLogger com barra")
    print("-" * 50)
    
    with ProgressLogger("Processando arquivos...", total=50) as progress:
        for i in range(50):
            time.sleep(0.05)
            progress.update(1)
    
    print("\n\nTeste 2: SimpleProgress")
    print("-" * 50)
    
    simple = SimpleProgress("Copiando arquivos...")
    for i in range(5):
        time.sleep(0.2)
        simple.step(f"Arquivo {i+1}.py")
    simple.done("Todos os arquivos copiados")

