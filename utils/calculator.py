import streamlit.components.v1 as components

def render_calculator():
    """
    Renders an offline HTML/JS/CSS based standard calculator.
    Because it runs entirely client-side, it will not trigger Streamlit reruns
    and is perfectly snappy, mimicking the CAT exam on-screen calculator.
    """
    calc_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .calculator {
            width: 240px;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
            font-family: Arial, sans-serif;
            margin: auto;
        }
        .display {
            width: 100%;
            height: 40px;
            font-size: 20px;
            text-align: right;
            margin-bottom: 10px;
            padding-right: 5px;
            border: 1px solid #aaa;
            background-color: #fff;
            box-sizing: border-box;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 5px;
        }
        button {
            height: 40px;
            font-size: 16px;
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #d0d0d0;
        }
        .btn-op {
            background-color: #f0a500;
            color: white;
            border: none;
        }
        .btn-op:hover {
            background-color: #d69300;
        }
        .btn-clear {
            background-color: #e74c3c;
            color: white;
            border: none;
            grid-column: span 2;
        }
        .btn-clear:hover {
            background-color: #c0392b;
        }
    </style>
    </head>
    <body>

    <div class="calculator">
        <input type="text" class="display" id="display" disabled value="0">
        <div class="buttons">
            <button class="btn-clear" onclick="clearDisplay()">C</button>
            <button onclick="appendDisplay('(')">(</button>
            <button onclick="appendDisplay(')')">)</button>
            
            <button onclick="appendDisplay('7')">7</button>
            <button onclick="appendDisplay('8')">8</button>
            <button onclick="appendDisplay('9')">9</button>
            <button class="btn-op" onclick="appendDisplay('/')">/</button>
            
            <button onclick="appendDisplay('4')">4</button>
            <button onclick="appendDisplay('5')">5</button>
            <button onclick="appendDisplay('6')">6</button>
            <button class="btn-op" onclick="appendDisplay('*')">*</button>
            
            <button onclick="appendDisplay('1')">1</button>
            <button onclick="appendDisplay('2')">2</button>
            <button onclick="appendDisplay('3')">3</button>
            <button class="btn-op" onclick="appendDisplay('-')">-</button>
            
            <button onclick="appendDisplay('0')">0</button>
            <button onclick="appendDisplay('.')">.</button>
            <button class="btn-op" onclick="calculate()">=</button>
            <button class="btn-op" onclick="appendDisplay('+')">+</button>
        </div>
    </div>

    <script>
        const display = document.getElementById('display');
        let currentInput = '0';

        function appendDisplay(value) {
            if (currentInput === '0' && value !== '.') {
                currentInput = value;
            } else {
                currentInput += value;
            }
            display.value = currentInput;
        }

        function clearDisplay() {
            currentInput = '0';
            display.value = currentInput;
        }

        function calculate() {
            try {
                // Using standard eval for a basic client side calculator. 
                // Safe here because input is strictly controlled by buttons.
                currentInput = eval(currentInput).toString();
                display.value = currentInput;
            } catch (error) {
                display.value = 'Error';
                currentInput = '0';
            }
        }
    </script>
    </body>
    </html>
    """
    components.html(calc_html, height=300)
