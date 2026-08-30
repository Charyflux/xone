#!/usr/bin/env python3
import http.server, socket, sys, os, webbrowser, threading

def find_free_port(candidates):
    for p in candidates:
        s = socket.socket()
        try:
            s.bind(('', p))
            s.close()
            return p
        except OSError:
            s.close()
    return None

PORT = find_free_port([7777, 7000, 9000, 6060, 5500, 4444, 3333, 8888])
if not PORT:
    print('[ERRO] Nenhuma porta livre encontrada.')
    sys.exit(1)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silencia logs de acesso

print(f'\n  ╔══════════════════════════════════╗')
print(f'  ║   AVEONE · AI BRAIN — JARVIS     ║')
print(f'  ║   http://localhost:{PORT}          ║')
print(f'  ╚══════════════════════════════════╝\n')
print(f'  Pressiona Ctrl+C para parar.\n')

def open_browser():
    import time; time.sleep(0.8)
    webbrowser.open(f'http://localhost:{PORT}')

threading.Thread(target=open_browser, daemon=True).start()

with http.server.HTTPServer(('', PORT), Handler) as srv:
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n  [JARVIS] Sistema encerrado.')
