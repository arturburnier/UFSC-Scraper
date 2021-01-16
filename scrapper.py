# CAGR SCRAPPER - Desenvolvido por Artur Burnier
# Licença - MIT

import html
import os
import re
import sys
from getpass import getpass

import requests
import unidecode
from bs4 import BeautifulSoup

# -----------------Vars
newlist = []
nome_curso = []
key = 0
match = 0
selection = 0

print("Digite seu login@ufsc: >", end='')
username = input()
password = getpass("Digite sua senha: >")

print('Autenticando...')

# -----------------Set work dir
dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
output_path = os.path.join(dir_path, 'output\\')
if not os.path.exists(dir_path):
    os.makedirs(dir_path)

# ------------------CAGR Session Login
URL = "https://sistemas.ufsc.br/login?service=https://idufsc.ufsc.br/auth"
session = requests.session()
texto = requests.get(URL)

regex = r"(?<=value=\")(?:.){600}(.*?)(?=\")"
matches = re.finditer(regex, texto.text, re.MULTILINE)

for match in matches:
    key = html.unescape(match.group())

payload = {'userType': 'padrao', 'username': username, 'password': password,
           'admin': '0', 'execution': key, "_eventId": 'submit'}

response = session.post(URL, data=payload)

status = response.status_code

if status == 200:
    print('Autenticado com sucesso!')
    print('Selecione a operação desejada: ')
    print(' 0 - Todos os cursos', ' 1 - Selecionar curso', ' > ', sep='\n', end='')
    selection = input()

elif status == 401:
    print('Falha na autenticação!')
    print('Precione qualquer tecla para sair.')
    input()
    exit()

else:
    print('Erro!')
    print('Precione qualquer tecla para sair.')
    input()
    exit()

# ------------------Import id e nome dos cursos
if selection == str(0):
    print('Selecionado - Todos os cursos')
    print('Carregando arquivos...')
    with open('cursos.txt', 'r', encoding='utf-8') as cursos:
        for line in cursos:
            newline = line.split(sep=',')
            newlist.append(newline)

    cod_curso, nome_curso_temp = zip(*newlist)

    for curso in nome_curso_temp:
        curso = re.sub(r'\n', r'', curso)
        nome_curso.append(curso)

else:
    print('Selecionado - Selecionar curso')
    print('Digite o código do curso desejado: > ', end='')
    cod_curso = input()

    print('Carregando arquivos...')
    with open('cursos.txt', 'r', encoding='utf-8') as cursos:
        for line in cursos:
            if cod_curso in line:
                newline = line.split(sep=',')
                newlist.append(newline)
            else:
                continue

    cod_curso, nome_curso_temp = zip(*newlist)

    for curso in nome_curso_temp:
        curso = re.sub(r'\n', r'', curso)
        nome_curso.append(curso)

# ------------------Scrapper CAGR (Nome, Matricula, Tipo, Curso, Codigo)
for cod, nome in zip(cod_curso, nome_curso):

    target_url = "http://forum.cagr.ufsc.br/listarMembros.jsf?salaId=100000" + str(cod)

    dados = session.get(target_url).text
    nome_decode = unidecode.unidecode(nome)
    file = cod + ' - ' + nome_decode + '.txt'
    print('[COD: {cod} - {curso}]   arquivo -> '.format(cod=cod, curso=nome), end='')
    print(file)
    output = open(output_path + file, 'w')

    dados_soup = BeautifulSoup(dados, 'html.parser')

    user_matricula = ['matricula']
    user_tipo = ['tipo']
    user_nome = ['nome']

    for tr in dados_soup.find_all('tr'):
        u_matricula = [td.text for td in tr.find_all('td', {'class': 'coluna2_listar_membros'})]
        user_matricula.append(u_matricula)

        u_tipo = [td.text for td in tr.find_all('td', {'class': 'coluna3_listar_membros'})]
        user_tipo.append(u_tipo)

        u_nome = [td.text for td in tr.find_all('td', {'class': 'coluna4_listar_membros'})]
        user_nome.append(u_nome)

    tabela_temp = []
    for um, un, ut in zip(user_matricula, user_nome, user_tipo):
        out = '{um};{un};{nome}'.format(um=um, un=un, nome=nome)
        out = re.sub(r']', '', out)
        out = re.sub(r'\[', '', out)
        out = re.sub(r"\'", '', out)
        print(out, file=output)
