import threading
import socket
import qrcode
import io
import base64
from flask import Flask, render_template_string, jsonify, request
from PyQt6.QtCore import QTimer

app = Flask(__name__)

filas_ref = {}
dia_atual_holder = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Fila do Almoço - Controle Remoto</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: white;
            min-height: 100vh;
            padding: 10px;
        }
        .header {
            text-align: center;
            padding: 15px 0;
            border-bottom: 2px solid #e94560;
            margin-bottom: 15px;
        }
        .header h1 {
            font-size: 22px;
            color: #e94560;
            letter-spacing: 2px;
        }
        .dia-atual {
            text-align: center;
            font-size: 14px;
            color: #4dabf7;
            margin-top: 5px;
        }
        .fila-card {
            background: #16213e;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .fila-titulo {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }
        .fila1-color { color: #4dabf7; }
        .fila2-color { color: #ff6b6b; }
        .status-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            background: #0a0a1a;
            padding: 10px;
            border-radius: 8px;
        }
        .status-label {
            font-size: 12px;
            color: #888;
        }
        .status-value {
            font-size: 20px;
            font-weight: bold;
        }
        .timer-display {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #00ff88;
            background: #0a0a1a;
            padding: 10px;
            border-radius: 10px;
            border: 2px solid #00ff88;
            margin-bottom: 10px;
        }
        .timer-display.pausa {
            color: #ffaa00;
            border-color: #ffaa00;
        }
        .turma-atual {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: white;
            background: #0a0a1a;
            padding: 8px;
            border-radius: 10px;
            margin-bottom: 8px;
        }
        .turma-proxima {
            text-align: center;
            font-size: 18px;
            color: #ccc;
            background: #0a0a1a;
            padding: 6px;
            border-radius: 8px;
            margin-bottom: 12px;
        }
        .botoes {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
        }
        .btn {
            padding: 14px 8px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            color: white;
            transition: transform 0.1s;
        }
        .btn:active { transform: scale(0.95); }
        .btn-iniciar { background: #2ecc71; }
        .btn-parar { background: #e74c3c; }
        .btn-chamar { background: #f39c12; }
        .info {
            text-align: center;
            color: #666;
            font-size: 11px;
            margin-top: 20px;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>FILA DO ALMOÇO</h1>
        <div class="dia-atual" id="dia-atual">Carregando...</div>
    </div>

    <div class="fila-card">
        <div class="fila-titulo fila1-color">FILA 1 - PRIMEIROS ANOS</div>
        <div class="timer-display" id="timer1">00:00</div>
        <div class="turma-atual" id="turma1">-</div>
        <div class="turma-proxima" id="proxima1">-</div>
        <div class="botoes">
            <button class="btn btn-iniciar" onclick="acao('fila1','iniciar')">INICIAR</button>
            <button class="btn btn-parar" onclick="acao('fila1','parar')">PARAR</button>
            <button class="btn btn-chamar" onclick="acao('fila1','chamar')">CHAMAR</button>
        </div>
    </div>

    <div class="fila-card">
        <div class="fila-titulo fila2-color">FILA 2 - SEGUNDOS E TERCEIROS ANOS</div>
        <div class="timer-display" id="timer2">00:00</div>
        <div class="turma-atual" id="turma2">-</div>
        <div class="turma-proxima" id="proxima2">-</div>
        <div class="botoes">
            <button class="btn btn-iniciar" onclick="acao('fila2','iniciar')">INICIAR</button>
            <button class="btn btn-parar" onclick="acao('fila2','parar')">PARAR</button>
            <button class="btn btn-chamar" onclick="acao('fila2','chamar')">CHAMAR</button>
        </div>
    </div>

    <div class="info">Controle remoto - Sistema de Fila do Almoço</div>

    <script>
        function acao(fila, acao) {
            fetch('/acao', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({fila: fila, acao: acao})
            });
        }

        function atualizar() {
            fetch('/status')
                .then(r => r.json())
                .then(d => {
                    document.getElementById('dia-atual').textContent = d.dia.toUpperCase();
                    for (let f of ['fila1', 'fila2']) {
                        let i = f === 'fila1' ? '1' : '2';
                        let info = d[f];
                        document.getElementById('timer' + i).textContent = info.timer;
                        let timerEl = document.getElementById('timer' + i);
                        timerEl.className = 'timer-display' + (info.em_pausa ? ' pausa' : '');
                        document.getElementById('turma' + i).textContent = info.turma_atual;
                        document.getElementById('proxima' + i).textContent = info.proxima_turma;
                    }
                })
                .catch(() => {});
        }

        setInterval(atualizar, 1000);
        atualizar();
    </script>
</body>
</html>
"""


def obter_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def gerar_qr_base64(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/status")
def status():
    resultado = {"dia": "segunda"}
    for nome_fila, fila in filas_ref.items():
        timer_text = "00:00"
        minutos = fila.tempo_restante // 60
        segundos = fila.tempo_restante % 60
        timer_text = f"{minutos:02d}:{segundos:02d}"

        turma_atual = "-"
        if fila.indice > 0 and fila.indice <= len(fila.turmas):
            turma_atual = fila.turmas[fila.indice - 1]

        proxima = "-"
        if fila.indice < len(fila.turmas):
            proxima = fila.turmas[fila.indice]
        else:
            proxima = "FIM"

        resultado[nome_fila] = {
            "timer": timer_text,
            "turma_atual": turma_atual,
            "proxima_turma": proxima,
            "em_pausa": fila.em_pausa,
            "timer_ativo": fila.timer_ativo,
        }

    if dia_atual_holder:
        resultado["dia"] = dia_atual_holder[0]()

    return jsonify(resultado)


@app.route("/acao", methods=["POST"])
def acao():
    dados = request.get_json()
    nome_fila = dados.get("fila")
    acao_nome = dados.get("acao")

    fila = filas_ref.get(nome_fila)
    if not fila:
        return jsonify({"erro": "fila nao encontrada"}), 404

    if acao_nome == "iniciar":
        QTimer.singleShot(0, fila.iniciar_timer)
    elif acao_nome == "parar":
        QTimer.singleShot(0, fila.parar_timer)
    elif acao_nome == "chamar":
        QTimer.singleShot(0, fila.chamar_turma)

    return jsonify({"ok": True})


class ServidorWeb:
    def __init__(self, port=5000):
        self.port = port
        self.thread = None
        self.url = None

    @staticmethod
    def _porta_livre(porta_inicial):
        porta = porta_inicial
        while porta < porta_inicial + 20:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(("0.0.0.0", porta))
                s.close()
                return porta
            except OSError:
                s.close()
                porta += 1
        return porta_inicial

    def iniciar(self):
        self.port = self._porta_livre(self.port)
        self.thread = threading.Thread(
            target=lambda: app.run(
                host="0.0.0.0", port=self.port, debug=False, use_reloader=False
            ),
            daemon=True,
        )
        self.thread.start()

        ip = obter_ip_local()
        url = f"http://{ip}:{self.port}"
        self.url = url
        print(f"\n{'='*50}")
        print(f"  SERVIDOR REMOTO ATIVO")
        print(f"  Acesse: {url}")
        print(f"{'='*50}\n")
        return url
