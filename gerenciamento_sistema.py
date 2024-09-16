from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Item():
    def __init__(self):
        self.dados = {}
        self.proximo_id = 1

    def criar(self, info, obrigatorio):
        if obrigatorio not in info:
            return None, 'Campo obrigatório não inserido'
        info['id'] = self.proximo_id
        self.dados[self.proximo_id] = info
        self.proximo_id += 1
        return info['id'], None

    def listar(self):
        return self.dados
    
    def especifico(self, id):
        return self.dados.get(id)
    
    def atualizar(self, id, info):
        if id in self.dados:
            self.dados[id].update(info)
            return True
        return False
    
    def deletar(self, id):
        return self.dados.pop(id, None) is not None
    
class APIHandler(BaseHTTPRequestHandler):
    books = Item()
    authors = Item()

    def _ler_json(self):
        tamanho = int(self.headers['Content-Length'])
        dados = self.rfile.read(tamanho)
        return json.loads(dados)

    def do_POST(self):
        if self.path == "/books":
            dados_requisicao = self._ler_json()
            id, error_msg = self.books.criar(dados_requisicao, "título")
        elif self.path == "/authors":
            dados_requisicao = self._ler_json()
            id, error_msg = self.authors.criar(dados_requisicao, "nome")
        else:
            self.send_response(404)
            self.end_headers()
            return

        if error_msg != None:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": error_msg}).encode())
        else:
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": id}).encode())

        

    def do_GET(self):
        entradaCorreta = False
        if self.path == "/books":
            entradaCorreta = True
            dados = self.books.listar()
        elif self.path == "/authors":
            entradaCorreta = True
            dados = self.authors.listar()
        if entradaCorreta:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(dados).encode())
            return
    
        if self.path.startswith('/books/'):
            try:
                item_id = int(self.path.split('/')[-1])
                item = self.books.especifico(item_id)
                entradaCorreta = True
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return
        elif self.path.startswith('/authors/'):
            try:
                item_id = int(self.path.split('/')[-1])
                item = self.authors.especifico(item_id)
                entradaCorreta = True
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return
        if entradaCorreta:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(item).encode())
            return
        
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
    