from flask import Flask, request, jsonify
import subprocess

app = Flask(_name_)
process = None

@app.route('/control', methods=['POST'])
def control_script():
    global process
    action = request.json.get('action')

    if action == 'start':
        if process is None or process.poll() is not None:  # Check if the script is not running
            process = subprocess.Popen(['python', 'cute1.py'])
            return jsonify({'status': 'Script started'})
        return jsonify({'status': 'Script is already running'})

    elif action == 'stop':
        if process and process.poll() is None:  # Check if the script is running
            process.terminate()
            return jsonify({'status': 'Script stopped'})
        return jsonify({'status': 'Script is not running'})

    return jsonify({'status': 'Invalid action'})

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000)