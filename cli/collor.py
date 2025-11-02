# saidas coloridas no terminal

# verde negrito
def green_bold(text):
    return f"\033[1;32m{text}\033[0m"

# vermelho negrito
def red_bold(text):
    return f"\033[1;31m{text}\033[0m"

# amarelo sem negrito
def yellow(text):
    return f"\033[0;33m{text}\033[0m"

# azul negrito
def blue_bold(text):
    return f"\033[1;34m{text}\033[0m"

# ciano negrito
def cyan_bold(text):
    return f"\033[1;36m{text}\033[0m"

if __name__ == "__main__":
    print(green_bold("Texto em verde negrito"))
    print(red_bold("Texto em vermelho negrito"))
    print(yellow("Texto em amarelo"))
    print(blue_bold("Texto em azul negrito"))
    print(cyan_bold("Texto em ciano negrito"))