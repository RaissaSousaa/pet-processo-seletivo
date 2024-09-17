from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Manipulação de livros e autores
class Item():
    def __init__(self):
        self.dados = {}
        self.proximo_id = 1
        self.campos_books = ["título", "gênero", "ano"] # Únicos campos aceitos em books
        self.campos_authors = ["nome", "data_nascimento", "nacionalidade"] # Únicos campos aceitos em authors

    def criar(self, info, obrigatorio):
        if obrigatorio not in info: # Obriga título para livros e nome para autores
            return None, "Campo obrigatório não inserido"
        if obrigatorio == "título": # Impede que livros sejam instanciados com campos diferentes dos pedidos
            for chave in info:
                if chave not in self.campos_books:
                    return None, "Campo inválido" 
        elif obrigatorio == "nome": # Impede que autores sejam instanciados com campos diferentes dos pedidos
            for chave in info:
                if chave not in self.campos_authors:
                    return None, "Campo inválido" 
        info['id'] = self.proximo_id # Gera id automaticamente
        self.dados[self.proximo_id] = info 
        self.proximo_id += 1
        return info['id'], None # Retorna livro ou autor criado

    def listar(self):
        return self.dados # Lista todos os livros ou autores
    
    def especifico(self, id):
        return self.dados.get(id) # Lista livro ou autor específico
    
    def atualizar(self, id, info):
        if id in self.dados: # Vê se existe livro ou ator com tal id para ser atualizado
            self.dados[id].update(info) # Atualiza livro ou autor
            return True 
        return False
    
    def deletar(self, id):
        return self.dados.pop(id, None) is not None # Deleta livro ou autor
    
class APIHandler(BaseHTTPRequestHandler):
    books = Item() 
    authors = Item()

    def _ler_json(self): # Converte json para dicionário
        tamanho = int(self.headers['Content-Length'])
        dados = self.rfile.read(tamanho)
        return json.loads(dados)

    def do_POST(self):
        if self.path == "/books": # Cria livro
            dados_requisicao = self._ler_json() # Converte json para dicionário
            id, error_msg = self.books.criar(dados_requisicao, "título")
        elif self.path == "/authors": # Cria autor
            dados_requisicao = self._ler_json() # Converte json para dicionário
            id, error_msg = self.authors.criar(dados_requisicao, "nome")
        else:
            self.send_response(404) # Not found
            self.end_headers()
            return

        if error_msg != None:
            self.send_response(400) # Bad request // erro de sintaxe
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": error_msg}).encode()) 
        else:
            self.send_response(201) # Created
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": id}).encode())

    def do_GET(self):
        entradaCorreta = False
        if self.path == "/books":
            entradaCorreta = True
            dados = self.books.listar() # Lista todos os livros
        elif self.path == "/authors":
            entradaCorreta = True
            dados = self.authors.listar() # Lista todos os autores
        if entradaCorreta:
            self.send_response(200) # Ok
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(dados).encode())
            return
    
        if self.path.startswith('/books/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url 
                item = self.books.especifico(id)
                entradaCorreta = True
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        elif self.path.startswith('/authors/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url 
                item = self.authors.especifico(id)
                entradaCorreta = True
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        if entradaCorreta:
            self.send_response(200) # Ok
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(item).encode())
            return
        
        self.send_response(404) # Not found
        self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/books/'):
            try:
                id = int(self.path.split('/')[-1]) # Id recebe como inteiro o último caractere do url
                dados_requisicao = self._ler_json()
                self.books.atualizar(id, dados_requisicao)
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        elif self.path.startswith('/authors/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url
                dados_requisicao = self._ler_json()
                self.authors.atualizar(id, dados_requisicao)
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        else:
            self.send_response(404) # Not found
            self.end_headers()
            return
        self.send_response(200) # Ok
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"messagem": "Informação atualizada"}).encode())
        
       

    def do_DELETE(self):
        if self.path.startswith('/books/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url
                self.books.deletar(id)
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        elif self.path.startswith('/authors/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url
                self.authors.deletar(id)
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        else:
            self.send_response(404) # Not found
            self.end_headers()
            return

        self.send_response(200) # Ok
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"messagem": "Item deletado"}).encode())

# Função para iniciar o servidor HTTP
def run(server_class=HTTPServer, handler_class=APIHandler, port=8000):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor rodando na porta {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
    