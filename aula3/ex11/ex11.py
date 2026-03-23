import pandas as pd

iterador_blocos = pd.read_csv('dados_sensor_gigante.csv', sep=',', na_values=['NA', '-'], chunksize=10)

for i, bloco in enumerate(iterador_blocos, start=1):
    media_temp = bloco['temperatura'].mean()
    valores_ausentes = bloco['temperatura'].isna().sum()

    print(f"--- Bloco {i} ---")
    print(f"Temperatura Média: {media_temp:.2f}")
    print(f"Valores Ausentes na Temperatura: {valores_ausentes}")
    print("-" * 30, "\n")




def analisador_lexico(expressao):
    tokens = []
    i = 0
    
    while i < len(expressao):
        char = expressao[i]

        if char.isspace():
            i += 1
            continue

        if char in "+-*/":
            tokens.append((char, 'operador'))
            i += 1
            continue

        if char == '(':
            tokens.append((char, 'abre_parenteses'))
            i += 1
            continue

        if char == ')':
            tokens.append((char, 'fecha_parenteses'))
            i += 1
            continue

        if char.isdigit():
            num_str = char
            i += 1
            is_real = False
            
            while i < len(expressao) and (expressao[i].isdigit() or expressao[i] == '.'):
                if expressao[i] == '.':
                    is_real = True
                num_str += expressao[i]
                i += 1
            
            if is_real:
                tokens.append((num_str, 'numero_real'))
            else:
                tokens.append((num_str, 'numero_inteiro'))
            continue

        i += 1

    return tokens