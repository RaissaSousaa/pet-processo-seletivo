from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Manipulação de livros e autores
class Item():
    def __init__(self):
        self.dados = {}
        self.proximo_id = 1
        self.campos_books = ["título", "gênero", "ano"] # Únicos campos aceitos para os livros
        self.campos_authors = ["nome", "data_nascimento", "nacionalidade"] # Únicos campos aceitos para os autores

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
    
    def associar(self, id_a, id_b):
        if id_b in self.dados: # Checa se o id do livro realmente existe
            if "autor_id" not in self.dados[id_b]: # Averigua se o livro já possui um autor associado a ele
                self.dados[id_b]["autor_id"] = id_a # Associa o id de um autor ao livro
                return self.dados[id_b], None
            else:
                return None, "Este livro já possui um autor"
        else:
            return None, "Este id de livro não existe"
        
    def listar_obras(self,id_a):
        obras = {} # Dicionário que ficará guardado as obras do autor
        for id in self.dados: # Percorre os livros registrados
            if "autor_id" in self.dados[id] and self.dados[id]["autor_id"] == id_a: # Confere se há associação de um autor com o livro e, caso haja, se é o autor desejado
                obras[id] = self.dados[id] # Adiciona o livro às obras do autor
        return obras
    
    def del_associacao(self,id_b):
        if id_b in self.dados and "autor_id" in self.dados[id_b]: # Verifica se o id do livro existe e se há um autor ligado a esse
            return self.dados[id_b].pop("autor_id",None) is not None # Retira a associação do autor com o livro

    
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
        elif self.path.startswith(f"/authors/"): # Checagem para mexer com associações
            try:
                id_b = int(self.path.split('/')[-1]) # id do livro recebe como inteiro o último caractere do url
                id_a = int(self.path.split('/')[-3]) # id do autor recebe como inteiro o antepenúltimo caractere do url
                info, error_msg = self.books.associar(id_a, id_b)
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        else:
            self.send_response(404) # Not found
            self.end_headers()
            return

        if error_msg != None:
            self.send_response(400) # Bad request // erro de sintaxe
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": error_msg}).encode()) 
        else:
            self.send_response(201) # Created
            self.send_header("Content-type", "application/json")
            self.end_headers()
            if self.path.startswith("/authors/"):
                self.wfile.write(json.dumps({f"{id_b}": info}).encode())
            else:
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
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(dados).encode())
            return
    
        if self.path.startswith("/books/"):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url 
                item = self.books.especifico(id) 
                entradaCorreta = True
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return

        elif self.path.startswith("/authors/"):
            if self.path.split("/")[-1] == "books": # Checagem para mexer com associações
                try:
                    id_a = int(self.path.split("/")[-2]) # id do autor recebe como inteiro o penúltimo caractere do url
                    item = self.books.listar_obras(id_a)
                    if item == {}:
                        item = {
                            "error": "Este autor não possui livros"
                        }
                    entradaCorreta = True
                except ValueError:
                    self.send_response(400) # Bad request // erro de sintaxe
                    self.end_headers()
                    return
            else: # Aqui lida-se apenas com os autores
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
            self.wfile.write(json.dumps(item).encode()) # Mostra livro ou autor específico *
            return
        
        self.send_response(404) # Not found
        self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/books/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url
                dados_requisicao = self._ler_json()
                self.books.atualizar(id, dados_requisicao) # Atualiza livro
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        elif self.path.startswith('/authors/'):
            try:
                id = int(self.path.split('/')[-1]) # id recebe como inteiro o último caractere do url
                dados_requisicao = self._ler_json()
                self.authors.atualizar(id, dados_requisicao) # Atualiza autor
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        else:
            self.send_response(404) # Not found
            self.end_headers()
            return
        self.send_response(200) # Ok
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"messagem": "Informação atualizada"}).encode())
        
    def do_DELETE(self):
        if self.path.startswith("/books/"):
            try:
                id = int(self.path.split("/")[-1]) # id recebe como inteiro o último caractere do url
                self.books.deletar(id) # Deleta livro
            except ValueError:
                self.send_response(400) # Bad request // erro de sintaxe
                self.end_headers()
                return
        elif self.path.startswith("/authors/"):
            if self.path.split("/")[-2] == "books": # Checagem para mexer com associações
                try:
                    id_b = int(self.path.split("/")[-1]) # id do livro recebe como inteiro o último caractere do url
                    self.books.del_associacao(id_b) # Deleta autor
                except ValueError:
                    self.send_response(400) # Bad request // erro de sintaxe
                    self.end_headers()
                    return
            else: # Aqui lida-se apenas com os autores
                try:
                    id = int(self.path.split("/")[-1]) # id recebe como inteiro o último caractere do url
                    self.authors.deletar(id) # Deleta autor
                except ValueError:
                    self.send_response(400) # Bad request // erro de sintaxe
                    self.end_headers()
                    return
        else:
            self.send_response(404) # Not found
            self.end_headers()
            return

        self.send_response(200) # Ok
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"messagem": "Item deletado"}).encode())

# Função para iniciar o servidor HTTP
def run(server_class=HTTPServer, handler_class=APIHandler, port=8000):
    server_address = ("localhost", port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor rodando na porta {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
    
