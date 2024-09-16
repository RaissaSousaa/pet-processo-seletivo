from http.server import HTTPServer, BaseHTTPRequestHandler
import json

authors = {
    1 : {"nome" : "Harlan Coben", "data_nascimento" : "04/01/1962", "nacionalidade" : "estadunidense"}
}

class APIHandler(BaseHTTPRequestHandler):
    def JSONparaDicionario(self):
        tamanho = int(self.headers['Content-Length'])
        dados = self.rfile.read(tamanho)
        dicionario = json.loads(dados)
        return dicionario
    
    def do_POST(self):
        if self.path == "/authors":
            author = self.JSONparaDicionario()
            if authors != {}:
                novo_id = max(authors.keys()) + 1
            else:
                novo_id = 1
            authors[novo_id] = author

            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"id": novo_id}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/authors":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(authors).encode())

        elif self.path.startswith('/authors/'):
            try:
                if authors == {}:
                    self.send_response(404)
                    self.end_headers()
                    return
                author_id = int(self.path.split('/')[-1])
                if author_id in authors:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(authors[author_id]).encode())
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
        if self.path.startswith('/authors/'):
            try:
                if authors == {}:
                    self.send_response(404)
                    self.end_headers()
                    return
                author_id = int(self.path.split('/')[-1])

                if author_id in authors:
                    authors[author_id] = self.JSONparaDicionario()

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'msg' : 'Autor atualizado'}).encode())
            
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
        if self.path.startswith('/authors/'):
            try:
                if authors == {}:
                    self.send_response(404)
                    self.end_headers()
                    return
                
                author_id = int(self.path.split('/')[-1])
                if author_id in authors:
                    del authors[author_id]

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"msg": "Autor deletado"}).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()

            except ValueError:
                self.send_response(400)
                self.end_headers()
                
        else:
                    self.send_response(404)
                    self.end_headers()        

    

                




servidor = HTTPServer(('localhost', 8000), APIHandler)
servidor.serve_forever()