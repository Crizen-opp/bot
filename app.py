<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Bot Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
        }
        h1 {
            color: #333;
        }
        .btn {
            display: inline-block;
            margin: 20px;
            padding: 10px 20px;
            font-size: 16px;
            color: white;
            background-color: #4CAF50;
            border: none;
            border-radius: 5px;
            text-decoration: none;
        }
        .btn:hover {
            background-color: #45a049;
        }
        .status {
            font-size: 18px;
            margin: 20px;
        }
        #logs {
            background-color: #f4f4f4;
            padding: 20px;
            margin-top: 20px;
            text-align: left;
            max-height: 300px;
            overflow-y: scroll;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        #logs p {
            margin: 5px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <h1>Telegram Bot Control Panel</h1>
    
    <!-- Bot Status Section -->
    <div class="status">
        <p><strong>Bot Status: </strong>
        {% if is_running %}
            <span style="color: green;">Running</span>
        {% else %}
            <span style="color: red;">Stopped</span>
        {% endif %}
        </p>
    </div>
    
    <!-- Buttons for starting and stopping the bot -->
    <div>
        <a href="{{ url_for('start') }}" class="btn">Start Bot</a>
        <a href="{{ url_for('stop') }}" class="btn">Stop Bot</a>
    </div>

    <!-- Logs Section (if any log message is available) -->
    <div>
        <h3>Bot Logs:</h3>
        <div id="logs">
            {% if bot_logs %}
                <p>{{ bot_logs }}</p>
            {% else %}
                <p>No logs available.</p>
            {% endif %}
        </div>
    </div>

</body>
</html>
