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

if __name__ == "__main__":
    print(green_bold("Texto em verde negrito"))
    print(red_bold("Texto em vermelho negrito"))
    print(yellow("Texto em amarelo"))