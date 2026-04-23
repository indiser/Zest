from flask import Flask, render_template, request, jsonify
import importlib
import multiprocessing
import os
import traceback

app = Flask(__name__)

# Reusing your safe worker logic to prevent the bot from crashing the web server
def worker(bot_name, fen, queue):
    try:
        module = importlib.import_module(bot_name)
        move = module.next_move(fen)
        queue.put(move)
    except Exception as e:
        # Stop wiping the fingerprints off the crime scene
        print(f"\n[FATAL ENGINE CRASH IN {bot_name}]:")
        traceback.print_exc() 
        queue.put(None)

def get_bot_move(bot_name, fen):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=worker, args=(bot_name, fen, queue))
    p.start()
    
    # Give the CPU a 10-second buffer to handle OS overhead. 
    # Your bot will still stop its math at 3.5 seconds internally.
    p.join(20) 
    
    if p.is_alive():
        print(f"\n[TIMEOUT] {bot_name} exceeded the 10-second hard limit and was killed.")
        p.terminate()
        return None
        
    if not queue.empty():
        return queue.get()
        
    return None

def get_available_bots():
    # Scan the current directory for all Python files except the server/engine scripts
    bots = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file not in ['app.py', 'engine.py']:
            bots.append(file[:-3]) # Strip the '.py' extension
    return sorted(bots)

@app.route('/')
def index():
    # Pass the dynamic list of bots to the HTML template
    return render_template('index.html', bots=get_available_bots())

@app.route('/bots')
def bots_arena():
    # Pass the dynamic list of bots to the Colosseum template
    return render_template('colosium.html', bots=get_available_bots())

@app.route('/play', methods=['POST'])
def play():
    data = request.json
    fen = data.get('fen')
    # Default to whatever bot was passed from the UI
    bot_name = data.get('bot') 
    
    bot_move_uci = get_bot_move(bot_name, fen)
    
    if bot_move_uci:
        return jsonify({"move": bot_move_uci})
    else:
        return jsonify({"error": "Bot failed or timed out"}), 500

if __name__ == '__main__':
    app.run(debug=True)

