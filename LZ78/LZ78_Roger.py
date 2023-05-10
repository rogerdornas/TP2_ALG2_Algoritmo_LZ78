##################################################################
'''
Autor: Roger Dornas Oliveira
Esse programa comprime e descomprime arquivos de texto pelo 
algoritmo LZ78, utilizando uma árvore trie como estrutura de dados
'''

##################################################################
import numpy as np
import math
import sys

##################################################################
#Classe Trie
class Node:
    def __init__(self):
        self.filhos = {}
        self.fim_de_palavra = False
        self.codigo = 0

class Trie:
    def __init__(self):
        self.root = Node()

    def inserir(self, word, ind):
        node = self.root
        for char in word:
            if char not in node.filhos:
                node.filhos[char] = Node()
            node = node.filhos[char]
        node.fim_de_palavra = True
        node.codigo = ind

    def busca(self, word):
        node = self.root
        for char in word:
            if char not in node.filhos:
                return (False, -1)
            node = node.filhos[char]
        return (node.fim_de_palavra, node.codigo)
    
##################################################################
#Função que lê os parâmetros passados por linha de comando
def ler_parametros(p):
    if(len(p) == 5):
        op = p[1]
        nome_file_in = p[2]
        nome_file_out = p[4]
    else:
        if(len(p) == 3):
            op = p[1]
            nome_file_in = p[2]
            if(op == "-c"):
                ind = nome_file_in.rfind('.')
                nome_file_out = nome_file_in[0:ind]
                nome_file_out += ".z78"
            else:
                if(op == "-x"):
                    ind = nome_file_in.rfind('.')
                    nome_file_out = nome_file_in[0:ind]
                    nome_file_out += ".txt"
    return(op, nome_file_in, nome_file_out)

##################################################################
#Função que comprime um arquivo usando o algoritmo LZ78
def compressao(nome_file_in, nome_file_out):
    trie = Trie() 

    #abrindo os arquivos
    file_in = open(nome_file_in, 'r', encoding=("utf8"))
    file_out = open(nome_file_out, 'wb')

    texto = file_in.read()
    
    #se o arquivo é vazio
    if(len(texto) == 0):
        num_bytes = 1
        num_bytes_char = 1
        file_out.write((int(num_bytes)).to_bytes(1, byteorder = 'big'))
        file_out.write((int(num_bytes_char)).to_bytes(1, byteorder = 'big'))
        return
    
    indice = 1
    trie.inserir("", 0)
    text = ""
    codigo = 0
    arr_cod = np.array([]) #array com os codigos da codificação
    arr_char = np.array([]) #array com os caracteres da codificação
    
    for c in texto:
        text += c
        existe, codigo_aux = trie.busca(text)
        if(existe):
            codigo = codigo_aux
        else:
            trie.inserir(text, indice)
            indice += 1
            text = ""
            arr_cod = np.concatenate((arr_cod, np.array([codigo])))
            arr_char = np.concatenate((arr_char, np.array([c])))
            codigo = 0

    #caso em que o último bloco lido já existe na árvore 
    if(len(text) > 0):
        arr_cod = np.concatenate((arr_cod, np.array([codigo])))
        arr_char = np.concatenate((arr_char, np.array([""])))
        
    #vetor com os valores unicode de arr_char
    arr_ord_char = np.empty(arr_char.shape)
    for i in range(arr_ord_char.shape[0]):
        if(arr_char[i] != ""):
            arr_ord_char[i] = ord(arr_char[i])
        else:
            arr_ord_char[i] = 0

    #número de bytes necessário para codificar os códigos
    max_cod = np.max(arr_cod) + 1
    num_bytes = math.log(max_cod, 2) / 8
    num_bytes = math.ceil(num_bytes)

    #número de bytes necessários para codificar os caracteres
    max_char = np.max(arr_ord_char) + 1
    num_bytes_char = math.log(max_char, 2) / 8
    num_bytes_char = math.ceil(num_bytes_char)
    
    #tratamento dos casos em que o arquivo de entrada possui menos de 3 caracteres
    if(num_bytes == 0):
        num_bytes = 1
    if(num_bytes_char == 0):
        num_bytes_char = 1
    
    #excrevendo no arquivo o número de bytes para os códigos e para os caracteres
    file_out.write((int(num_bytes)).to_bytes(1, byteorder = 'big'))
    file_out.write((int(num_bytes_char)).to_bytes(1, byteorder = 'big'))
    
    #gravando no arquivo de saída o texto comprimido
    for i in range(arr_cod.shape[0]):
        file_out.write((int(arr_cod[i])).to_bytes(num_bytes, byteorder = 'big'))
        if(arr_char[i] != ""):
            file_out.write((int(arr_ord_char[i])).to_bytes(num_bytes_char, byteorder = 'big'))
    
    #fechando os arquivos
    file_in.close()
    file_out.close()

##################################################################
#Função que descomprime um arquivo usando o algoritmo LZ78
def descompressao(nome_file_in, nome_file_out):
    Dict = {}
    Dict[0] = ""
    
    #abrindo os arquivos
    file_in = open(nome_file_in, "rb")
    file_out = open(nome_file_out, "w", encoding=("utf8"))
    
    #lendo do arquivo o número de bytes usados para o código
    num_bytes = file_in.read(1)
    num_bytes = int.from_bytes(num_bytes, byteorder = 'big')

    #lendo do arquivo o número de bytes usados para o caractere
    num_bytes_char = file_in.read(1)
    num_bytes_char = int.from_bytes(num_bytes_char, byteorder = 'big')
    
    indice = 1
    text = ""
    codigo = 0
    saida = ""
    
    while(1):
        codigo = file_in.read(num_bytes)
        if(codigo == b''): #se o arquivo acabou
            break
        codigo = int.from_bytes(codigo, byteorder ='big')
        text = file_in.read(num_bytes_char)
        if(text != b''):  
            text = int.from_bytes(text, byteorder ='big')
            text = chr(text)
            saida = saida + Dict[codigo] + text
            Dict[indice] = Dict[codigo] + text
        else:
            saida = saida + Dict[codigo]
        indice += 1
        
    #gravando no arquivo de saída o texto descomprimido
    file_out.write(saida)
    
    #fechando os arquivos
    file_in.close()
    file_out.close()

##################################################################
#Programa principal
param = sys.argv
op, nome_file_in, nome_file_out = ler_parametros(param)

if(op == "-c"):
    compressao(nome_file_in, nome_file_out)
if(op == "-x"):
    descompressao(nome_file_in, nome_file_out)
