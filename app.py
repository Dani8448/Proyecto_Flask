from flask import Flask, render_template, request, abort
import json
import os

app = Flask(__name__)

def load_data():

    base_path = os.path.dirname(__file__)
    ruta_json = os.path.join(base_path, 'data', 'videojuegos.json')
    
    try:
        with open(ruta_json, encoding='utf-8') as f:
            datos = json.load(f)
            return datos.get('videojuegos', [])
    except Exception as e:
        print(f"Error crítico cargando el JSON: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/juegos')
def juegos():
    todos = load_data()
    
    for i, g in enumerate(todos):
        g['_id'] = i

    q      = request.args.get('q', '').strip()
    genero = request.args.get('genero', '').strip()
    orden  = request.args.get('orden', 'asc').strip()

    # Obtener lista de géneros únicos de forma segura
    generos_set = set()
    for j in todos:
        g_list = j.get('genero', [])
        if isinstance(g_list, list):
            generos_set.update(g_list)
        else:
            generos_set.add(g_list)
    lista_generos = sorted(list(generos_set))

    resultado = todos[:]
    if q:
        resultado = [j for j in resultado if q.lower() in j.get('titulo', '').lower()]
    
    if genero:
        resultado = [j for j in resultado if genero in j.get('genero', [])]


    resultado = sorted(resultado, key=lambda j: j.get('titulo', '').lower(), reverse=(orden == 'desc'))

    return render_template('juegos.html', 
                           juegos=resultado, 
                           generos=lista_generos,
                           q=q, 
                           genero=genero, 
                           orden=orden)

@app.route('/juego/<int:jid>')
def detalle(jid):
    todos = load_data()
    if jid < 0 or jid >= len(todos):
        abort(404)
    
    juego = todos[jid]
    
    v = juego.get('ventas', {})
    total = v.get('europa', 0) + v.get('america', 0) + v.get('japon', 0)
    
    vals = juego.get('valoraciones', {}).get('usuarios', [])
    media = round(sum(vals) / len(vals), 1) if vals else "N/A"
    
    return render_template('detalle.html', 
                           juego=juego, 
                           jid=jid, 
                           total_ventas=total, 
                           media_usuarios=media)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    # debug=True es vital ahora mismo para ver errores si algo falla
    app.run(host='0.0.0.0', port=5000, debug=True)
