# Genera la web: copia los archivos y crea una carpeta /x/<id>/ con su propio
# index.html y manifest.json para cada sorteo activo. Asi cada sorteo se instala
# en el movil como una app distinta, con el nombre de su serie.
import json, os, shutil, urllib.request, hashlib, sys

API = 'https://script.google.com/macros/s/AKfycbyaLjO7lrZktZVERB6Fxvaq8DengZpBiEQSJ96R7iyMWwXbxQSy8i8Klo7g51-PqdX1Ig/exec?action=lista'
SKIP = {'.git', '.github', '_site', '.ultima-lista', 'build.py', 'README.md'}

data = json.load(urllib.request.urlopen(API, timeout=60))
if not data.get('ok'):
    sys.exit('La API no ha devuelto la lista: %s' % data)
sorteos = data['sorteos']

if len(sys.argv) > 1 and sys.argv[1] == 'hash':
    print(hashlib.sha1(json.dumps(sorteos, sort_keys=True).encode()).hexdigest()[:16])
    sys.exit()

shutil.rmtree('_site', ignore_errors=True)
os.makedirs('_site')
for f in os.listdir('.'):
    if f in SKIP:
        continue
    if os.path.isdir(f):
        shutil.copytree(f, os.path.join('_site', f))
    else:
        shutil.copy2(f, os.path.join('_site', f))

index = open('index.html', encoding='utf-8').read()
for s in sorteos:
    sid = ''.join(c for c in s['id'] if c.isalnum() or c == '-')
    nombre = (s.get('nombre') or 'Sorteo').strip()[:40] or 'Sorteo'
    d = os.path.join('_site', 'x', sid)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(index)
    url = '/sorteo/x/%s/' % sid
    man = {
        'id': url, 'name': nombre, 'short_name': nombre,
        'description': 'Sorteo de Navidad de ' + nombre,
        'start_url': url, 'scope': url, 'display': 'standalone',
        'background_color': '#0f3d2b', 'theme_color': '#0f3d2b', 'lang': 'es',
        'icons': [
            {'src': '/sorteo/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': '/sorteo/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': '/sorteo/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }
    with open(os.path.join(d, 'manifest.json'), 'w', encoding='utf-8') as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1)
    print('Sorteo', sid, '->', nombre)
