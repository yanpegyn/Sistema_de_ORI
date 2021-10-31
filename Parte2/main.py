from math import log10
from tabulate import tabulate

# O fitz faz parte do PyMuPDF
import fitz

# Armazena a quantidade de documentos
n_docs_total = 0
presentes_em = []


# Formata o número de documentos e a quantidade
def quebrar_doc(doc):
    arr = list(map(int, doc.split("/")))
    global n_docs_total
    if arr[0] > n_docs_total:
        n_docs_total = arr[0]
    return {
        "n_doc": arr[0],
        "qtd": arr[1]
    }


# Transforma o indíce invertido em objeto
def quebrar_indice(linha):
    primeira_barra = linha.find("/")
    primeiro_espaco = linha.find(" ")
    segunda_parte = linha[linha.find(">") + 2:-1].split(", ")
    obj = {
        "palavra": linha[0:primeira_barra],
        "qtd_docs": int(linha[primeira_barra + 1:primeiro_espaco]),
        "docs": list(map(lambda doc: quebrar_doc(doc), segunda_parte))
    }
    return obj


# Lê o arquivo de indice invertido
def ler(name):
    arquivo = open(name + ".txt", 'r', encoding="utf8")
    indice = 0
    indiceInvertido = []  # palavra/qtd_docs -> n_doc/qtd_vezes
    for linha in arquivo:
        if linha == "Indice invertido:\n":
            indice = 1
        elif indice > 0:
            indice += 1
            if indice > 2:
                indiceInvertido.append(quebrar_indice(linha))
    arquivo.close()
    return indiceInvertido


# Calcula o IDF de uma palavra
def calc_idf(obj):
    global n_docs_total
    obj["IDF"] = log10(n_docs_total / obj["qtd_docs"])


# Calcula o W de uma palavra em um documento
def calc_w(doc):
    doc["W"] = (1 + log10(doc["qtd"])) if doc["qtd"] > 0 else 0


# Calcula o TF_IDF de uma palavra em um documento
def calc_tf_idf(doc, idf):
    doc["TF.IDF"] = doc["W"] * idf


# Cria a lista de quais documentos as palavras estão presentes
def docs_presentes(indiceInvertido):
    lista = []
    for obj in indiceInvertido:
        for doc in obj["docs"]:
            lista.append(doc["n_doc"])
    return sorted(list(set(lista)))


# Monta lista do vetor de constante (pega os IDFs tudo)
def monta_vcons(indiceInvertido):
    idfs = []
    for obj in indiceInvertido:
        idfs.append(obj["IDF"])
    return idfs


# Monta cada vetor de documentos
def monta_vdoc(indiceInvertido):
    global n_docs_total, presentes_em
    presentes_em = docs_presentes(indiceInvertido)
    vdocs = {}
    aux = [[0 for x in range(len(indiceInvertido))] for y in range(len(presentes_em))]
    linha = 0
    for obj in indiceInvertido:
        coluna = 0
        for pn_doc in presentes_em:
            for doc in obj["docs"]:
                if doc["n_doc"] == pn_doc:
                    aux[coluna][linha] = doc["TF.IDF"]
            coluna += 1
        linha += 1
    for line, pn_doc in zip(aux, presentes_em):
        vdocs["Vdoc{}".format(pn_doc)] = line
    vdocs["Vcons"] = monta_vcons(indiceInvertido)
    return vdocs


# Calcula o módulo de cada um dos documentos
def monta_mdoc(vdocs):
    global n_docs_total, presentes_em
    mdocs = {}
    for n_doc in presentes_em:
        mdocs["Mdoc{}".format(n_doc)] = (sum(list(map(lambda e: e ** 2, vdocs["Vdoc{}".format(n_doc)]))) ** 0.5)
    mdocs["Mcons"] = (sum(list(map(lambda e: e ** 2, vdocs["Vcons"]))) ** 0.5)
    return mdocs


# Normaliza os vetores de documentos
def monta_vdoc_normalizado(vdocs, mdocs):
    global n_docs_total, presentes_em
    vdocsn = {}
    for n_doc in presentes_em:
        if mdocs["Mdoc{}".format(n_doc)] != 0:
            vdocsn["Vdoc{}n".format(n_doc)] = list(
                map(lambda e: e / mdocs["Mdoc{}".format(n_doc)], vdocs["Vdoc{}".format(n_doc)]))
    if mdocs["Mcons"] != 0:
        vdocsn["Vconsn"] = list(map(lambda e: e / mdocs["Mcons"], vdocs["Vcons"]))
    return vdocsn


# Calcula os cossenos
def calcula_cossenos(vdocsn):
    global n_docs_total, presentes_em
    cos = {}
    vconsn = vdocsn['Vconsn']
    for n_doc in presentes_em:
        temp = 0
        for i in range(len(vconsn)):
             temp += vdocsn["Vdoc{}n".format(n_doc)][i] * vconsn[i]
        cos["CosDoc{}nconsn".format(n_doc)] = temp
    return cos


# Lê a lista de documentos e converte para objetos
def ler_lista_docs(name):
    arquivo = open(name + ".txt", 'r', encoding="utf8")
    lista = arquivo.readline()
    arquivo.close()
    lista = lista[lista.find(":") + 2:-1].split("; ")
    keys = []
    values = []
    for doc in lista:
        keys.append(int(doc.split("/")[0]))
        values.append(doc.split("/")[1])
    lista = dict(zip(keys, values))
    return lista


# Busca o sumário (10 palavras cada)
def ler_sumario(titulo):
    sumario = ""
    with fitz.open(titulo) as pdf:
        for pagina in pdf:
            texto = pagina.get_text()
            indice = 0
            palavras = 0
            anterior = False
            c_ant = ""
            for caracter in texto:
                if not caracter.isalnum() and not anterior and c_ant.isalnum():
                    palavras += 1
                    anterior = True
                elif c_ant.isalnum() != caracter.isalnum():
                    anterior = False
                indice += 1
                if palavras == 10:
                    break
                c_ant = caracter
            sumario = texto[0:indice]
            break
        pdf.close()
    return sumario


# Rankear os documentos (pelos cossenos)
def rankear(linhas):
    return sorted(linhas, key=lambda x: x[3], reverse=True)


# Formata as linhas para a tabela
def monta_linhas_print(lista_docs, cos):
    headers = ["n_doc", "Título", "Sumário", "Score"]
    linhas = []
    for doc in lista_docs:
        try:
            linhas.append(
                [doc, lista_docs[doc], ler_sumario(lista_docs[doc]), float(cos["CosDoc{}nconsn".format(doc)])])
        except KeyError:
            continue
    return [headers] + rankear(linhas)


# Roda o programa
if __name__ == '__main__':
    debug = False
    indiceInvertido = ler('resposta')
    print("Docs total: {}".format(n_docs_total))
    for obj in indiceInvertido:
        calc_idf(obj)
        for doc in obj["docs"]:
            calc_w(doc)
            calc_tf_idf(doc, obj["IDF"])
    print("\tPalavras: ", end="")
    for obj in indiceInvertido:
        print("" + obj["palavra"], end=";")
    print("\n\n")
    palavras = input("Insira as palavras a serem buscadas quebrando com ';': ").split(";")
    indiceInvertido = list(filter(lambda p: p["palavra"] in palavras, indiceInvertido))
    if len(indiceInvertido) == 0:
        print("Palavras não encontradas!!!")
    else:
        vdocs = monta_vdoc(indiceInvertido)
        mdocs = monta_mdoc(vdocs)
        vdocsn = monta_vdoc_normalizado(vdocs, mdocs)
        cos = calcula_cossenos(vdocsn)
        lista_docs = ler_lista_docs('resposta')
        if debug:
            print("Indice Invertido:")
            print(indiceInvertido)
            print("Vdocs:")
            print(vdocs)
            print("Mdocs:")
            print(mdocs)
            print("Vdocsn:")
            print(vdocsn)
            print("Cos:")
            print(cos)
            print("\n\n\n")
        print(tabulate(monta_linhas_print(lista_docs, cos), headers='firstrow', tablefmt='fancy_grid'))
