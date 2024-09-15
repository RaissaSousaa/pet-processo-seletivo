from http.server import HTTPServer, SimpleHTTPRequestHandler

servidor = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
servidor.serve_forever()