# re de Regex
import re

# O fitz faz parte do PyMuPDF
import fitz


def read(name):
    # Pega as Stopwords possíveis
    stopwords_arq = open("stopwords.txt", "r", encoding='UTF-8')
    stopwords_possiveis = stopwords_arq.read().split("\n")
    # Lê o pdf usando o fitz do PyMuPDF
    with fitz.open(name) as pdf:
        stopwords_encontradas = []
        lista = []
        # Para cada página, lê o texto, transforma tudo para minusculo, remove os símbolos
        # Logo após pega as palavras como lista e remove as palavras vazias
        # Procura as palavras que estão lista que são stopwords
        for pagina in pdf:
            lista += re.sub(r'[^A-ZÀ-Úa-zà-ú0-9 ]+', '', pagina.getText().lower()).split(" ")
            lista = list(filter(lambda a: a != "", lista))
            stopwords_encontradas += [s for s in lista if s in stopwords_possiveis]
        # Remove as repetições
        stopwords_encontradas = list(set(stopwords_encontradas))
        # Tira stopwords da lista
        lista = [s for s in lista if s not in stopwords_encontradas]
        # Normaliza as palavras
        for i in range(len(lista)):
            lista[i] = lista[i].replace("quinhos", "co")
            lista[i] = lista[i].replace("rinhos", "ro")
            lista[i] = lista[i].replace("chinha", "cho")
            lista[i] = lista[i].replace("ininho", "ino")
            lista[i] = lista[i].replace("morta", "morto")
            lista[i] = lista[i].replace("feita", "feito")
            lista[i] = lista[i].replace("viva", "vivo")
            lista[i] = lista[i].replace("cozinheira", "cozinheiro")
            lista[i] = lista[i].replace("aberta", "aberto")
            lista[i] = lista[i].replace("devagarinho", "devagar")
            lista[i] = lista[i].replace("prazenteira", "prazenteiro")
            lista[i] = lista[i].replace("dura", "duro")
            lista[i] = lista[i].replace("redonda", "redondo")
            lista[i] = lista[i].replace("azuis", "azul")
            lista[i] = lista[i].replace("branca", "branco")
            lista[i] = lista[i].replace("amarelinhas", "amarelo")
            lista[i] = lista[i].replace("amarela", "amarelo")
            lista[i] = lista[i].replace("preta", "preto")
            lista[i] = lista[i].replace("franca", "fraco")
            lista[i] = lista[i].replace("bonitinhas", "bonito")
            lista[i] = lista[i].replace("nova", "novo")
            lista[i] = lista[i].replace("grandão", "grande")
            lista[i] = lista[i] if lista[i][-1] != 's' else lista[i][:-1]
        # Tira stopwords da lista e atualiza as stopwords encontradas
        stopwords_encontradas += [s for s in lista if s in stopwords_possiveis]
        lista = [s for s in lista if s not in stopwords_possiveis]
        # Cria um dicionário key-value de palavra e quantas vezes a mesma apareceu
        palavras_qtd = {s: lista.count(s) for s in lista}
        # Monta um dicionário estilo JSON para retornar as informações obtidas pela função
        resultado = {
            'stopwords': stopwords_encontradas,
            'palavras_qtd': palavras_qtd,
            'nome': name
        }
        # Fecha o PDF
        pdf.close()
        # Retorna os resultados
        return resultado


# Une todas as listas de stopwords do objeto de resultados e remove as repetições
def une_stopwords(resultados):
    return list(set([s for sbl in list(map(lambda r: r['stopwords'], resultados)) for s in sbl]))


# Retorna uma lista ordenada de palavras
# Para isso a função une todas as listas de palavras do objeto de resultados e remove as repetições
def une_palavras(resultados):
    return sorted(
        list(set([s for sbl in list(map(lambda r: list(r['palavras_qtd'].keys()), resultados)) for s in sbl])))


def calcula_indice_invertido(palavras, resultados):
    # Cria um dicionário estilo JSON que para cada palavra há seus sub-valores
    repeticoes = {s: {'qtd_docs_apareceu': 0, 'docs': []} for s in palavras}
    # Para cada indice e resultado
    for i_r, r in enumerate(resultados):
        # Para cada palavra
        for p in palavras:
            # Conta quantas vezes a palavra apareceu nesse resultado, com a tratativa para não ocorrer erro de key
            apareceu = 0 if p not in list(r['palavras_qtd'].keys()) else r['palavras_qtd'][p]
            # Se apareceu
            if apareceu > 0:
                # Incrementa a quantidade de documentos que a palavra apareceu
                repeticoes[p]['qtd_docs_apareceu'] += 1
                # Salva o codigo do documento que a palavra apareceu e a quantidade de vezes
                repeticoes[p]['docs'].append({
                    'codigo': "{}/{}".format(i_r + 1, r['nome']),
                    'qtd': apareceu
                })
    # Retorna o dicionário
    return repeticoes


# Transforma o dicionário da função calcula_indice_invertido em String
def formata_indice_invertido(obj_indice_invertido):
    # palavra/qtd_docs_apareceu -> documento/qtd_no_documento, ...
    texto = "Indice invertido:\n\n"
    for palavra in obj_indice_invertido:
        obj = obj_indice_invertido[palavra]
        str_palavra = ""
        str_palavra_qtd = "{}/{} ->".format(palavra, obj['qtd_docs_apareceu'])
        str_palavra += str_palavra_qtd
        str_onde_qtd = ""
        for doc in obj['docs']:
            str_onde_qtd += " {}/{},".format(doc['codigo'].split("/")[0], doc['qtd'])
        str_palavra += str_onde_qtd[:-1]
        texto += "{}\n".format(str_palavra)
    return texto


# Cria a lista de documentos conforme a lista de nomes
def formata_lista_documentos(nomes):
    texto = "Lista de documentos:"
    for i, n in enumerate(nomes):
        texto += " {}/{};".format(i+1, n)
    return texto[:-1]


# Transforma em string a lista de stopwords
def formata_stopwords(stopwords):
    texto = "As stopwords encontradas foram:\n\n"
    for s in stopwords:
        texto += "{}\n".format(s)
    return texto


if __name__ == '__main__':
    # Lista de documentos a ser analisado
    nomes = [
        'A_Canção_dos_tamanquinhos_Cecília_Meireles.pdf',
        'A_Centopeia_Marina_Colasanti.pdf',
        'A_porta_Vinicius_de_Moraes.pdf',
        'Ao_pé_de_sua_criança_Pablo_Neruda.pdf',
        'As_borboletas_Vinicius_de_Moraes.pdf',
        'Convite_José_Paulo_Paes.pdf',
        'Pontinho_de_Vista_Pedro_Bandeira.pdf'
    ]
    # Executa os resultados para cada arquivo
    resultados = [read(n) for n in nomes]
    # Converte os resuldados para os textos que serão escritos nos arquivos
    stopwords = une_stopwords(resultados)
    palavras = une_palavras(resultados)
    obj_indice_invertido = calcula_indice_invertido(palavras, resultados)
    str_indice_invertido = formata_indice_invertido(obj_indice_invertido)
    str_lista_documentos = formata_lista_documentos(nomes)
    str_stopwords = formata_stopwords(stopwords)
    # Escreve a lista de documentos e o indice invertido no arquivo resposta.txt
    with open('resposta.txt', 'w', encoding='UTF-8') as txt:
        txt.write(str_lista_documentos)
        txt.write("\n\n------------------------------------------\n\n")
        txt.write(str_indice_invertido)
        txt.close()
    # Escreve as stopwords encontradas na arquivo stopwords_encontradas.txt
    with open('stopwords_encontradas.txt', 'w', encoding='UTF-8') as txt:
        txt.write(str_stopwords)
        txt.close()
