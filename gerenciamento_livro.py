from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Classe para gerenciar livros
class Livro:
    def __init__(self):
        self.livros = {}
        self.proximo_id = 1

    def criar_livro(self, dados_livro):
        if 'título' not in dados_livro:
            return None, "Campo 'título' é obrigatório"
        dados_livro['id'] = self.proximo_id
        self.livros[self.proximo_id] = dados_livro
        self.proximo_id += 1
        return dados_livro['id'], None

    def listar_livros(self):
        return self.livros

    def obter_detalhes_livro(self, book_id):
        return self.livros.get(book_id)

    def atualizar_livro(self, book_id, dados_livro):
        if book_id in self.livros:
            # Atualiza o livro existente com novos dados
            self.livros[book_id].update(dados_livro)
            return True
        return False

    def remover_livro(self, book_id):
        return self.livros.pop(book_id, None) is not None

# Handler para processar requisições HTTP
class APIHandler(BaseHTTPRequestHandler):
    manager = Livro()

    def _ler_json(self):
        tamanho = int(self.headers['Content-Length'])
        dados = self.rfile.read(tamanho)
        return json.loads(dados)

    def do_POST(self):
        if self.path == "/books":
            dados_requisicao = self._ler_json()
            book_id, error = self.manager.criar_livro(dados_requisicao)
            if error:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": error}).encode())
            else:
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"id": book_id}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/books":
            livros = self.manager.listar_livros()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(livros).encode())
        elif self.path.startswith('/books/'):
            try:
                book_id = int(self.path.split('/')[-1])
                livro = self.manager.obter_detalhes_livro(book_id)
                if livro:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(livro).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            except ValueError:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/books/'):
            try:
                book_id = int(self.path.split('/')[-1])
                dados_requisicao = self._ler_json()
                if self.manager.atualizar_livro(book_id, dados_requisicao):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"messagem": "Livro atualizado"}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            except ValueError:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/books/'):
            try:
                book_id = int(self.path.split('/')[-1])
                if self.manager.remover_livro(book_id):
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"messagem": "Livro deletado"}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            except ValueError:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

# Função para iniciar o servidor HTTP
def run(server_class=HTTPServer, handler_class=APIHandler, port=8000):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    print(f"Servidor rodando na porta {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()