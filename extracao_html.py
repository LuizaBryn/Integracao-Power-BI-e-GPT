from bs4 import BeautifulSoup
import requests

header = {'user-agent': 'Mozilla/5.0'}
requisicao = requests.get('https://www.ciasc.sc.gov.br/produtos-e-servicos/', 
                          headers = header)
conteudo = requisicao.text
site = BeautifulSoup(conteudo, 'html.parser')
html = site.find('html')
html = str(html)

with open("site.html", "w", encoding="utf-8") as arquivo:
    arquivo.write(html)