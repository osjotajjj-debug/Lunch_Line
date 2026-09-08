import sys
import threading
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton, QTabBar,
                              QStackedWidget, QLineEdit, QSpinBox, QListWidget,
                              QListWidgetItem, QMessageBox, QScrollArea, QFrame,
                              QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
import winsound
import yaml
import comtypes.client

from web_server import ServidorWeb, gerar_qr_base64, filas_ref, dia_atual_holder


CONFIG_PATH = Path(__file__).parent / "config.yaml"

CONFIG_PADRAO = {
    "turmas": {
        "segunda": {"fila1": ["1A", "1B", "1C", "1D"], "fila2": ["2A", "2B", "3A", "3B"]},
        "terca": {"fila1": ["1B", "1C", "1D", "1A"], "fila2": ["2B", "3A", "3B", "2A"]},
        "quarta": {"fila1": ["1C", "1D", "1A", "1B"], "fila2": ["3A", "3B", "2A", "2B"]},
        "quinta": {"fila1": ["1D", "1A", "1B", "1C"], "fila2": ["3B", "2A", "2B", "3A"]},
        "sexta": {"fila1": ["1A", "1B", "1C", "1D"], "fila2": ["2A", "2B", "3A", "3B"]},
    },
    "timer": {"segundos": 30, "pausa_entre_chamadas": 5},
}


def carregar_config():
    if not CONFIG_PATH.exists():
        salvar_config(CONFIG_PADRAO)
        return CONFIG_PADRAO.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if not config or "turmas" not in config or "timer" not in config:
            return CONFIG_PADRAO.copy()
        return config
    except (yaml.YAMLError, OSError):
        return CONFIG_PADRAO.copy()


def salvar_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


ESTILO_APP = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: white;
}
QTabBar::tab {
    padding: 12px 30px;
    font-size: 18px;
    font-weight: bold;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
QTabBar::tab:selected {
    background-color: #e94560;
    color: white;
}
QTabBar::tab:!selected {
    background-color: #16213e;
    color: #a0a0a0;
}
QPushButton {
    background-color: #0f3460;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: bold;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #e94560;
}
QPushButton:pressed {
    background-color: #c23152;
}
QLineEdit {
    background-color: #0a0a1a;
    color: white;
    border: 2px solid #444;
    border-radius: 6px;
    padding: 8px;
    font-size: 16px;
}
QLineEdit:focus {
    border: 2px solid #e94560;
}
QSpinBox {
    background-color: #0a0a1a;
    color: white;
    border: 2px solid #444;
    border-radius: 6px;
    padding: 8px;
    font-size: 16px;
}
QSpinBox:focus {
    border: 2px solid #e94560;
}
QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 24px;
    height: 24px;
    border-left: 1px solid #444;
    border-bottom: 1px solid #444;
    border-top-right-radius: 6px;
    background-color: #16213e;
}
QSpinBox::up-button:hover {
    background-color: #0f3460;
}
QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 24px;
    height: 24px;
    border-left: 1px solid #444;
    border-top: 1px solid #444;
    border-bottom-right-radius: 6px;
    background-color: #16213e;
}
QSpinBox::down-button:hover {
    background-color: #0f3460;
}
QSpinBox::up-arrow, QSpinBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox {
    background-color: #0a0a1a;
    color: white;
    border: 2px solid #444;
    border-radius: 6px;
    padding: 8px;
    font-size: 16px;
}
QComboBox:hover {
    border: 2px solid #e94560;
}
QComboBox::drop-down {
    border-left: 1px solid #444;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #0a0a1a;
    color: white;
    border: 2px solid #444;
    selection-background-color: #e94560;
}
QListWidget {
    background-color: #0a0a1a;
    color: white;
    border: 2px solid #444;
    border-radius: 6px;
    font-size: 16px;
    padding: 4px;
}
QListWidget::item {
    padding: 6px;
}
QListWidget::item:selected {
    background-color: #e94560;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 12px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #444;
    border-radius: 6px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #e94560;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


class FilaPanel(QWidget):
    def __init__(self, nome_fila, cor, turmas, tempo_total, pausa_entre_chamadas=5):
        super().__init__()
        self.nome_fila = nome_fila
        self.cor = cor
        self.turmas = turmas
        self.tempo_total = tempo_total
        self.pausa_entre_chamadas = pausa_entre_chamadas
        self.indice = 0
        self.tempo_restante = 0
        self.timer_ativo = False
        self.em_pausa = False

        self.init_ui()

        self.timer_qt = QTimer()
        self.timer_qt.timeout.connect(self.atualizar_timer)

    def init_ui(self):
        self.setStyleSheet("background-color: #16213e; border-radius: 12px;")

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label_titulo = QLabel(self.nome_fila)
        self.label_titulo.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {self.cor}; background: transparent;")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_titulo)

        separador = QLabel()
        separador.setFixedHeight(3)
        separador.setStyleSheet(f"background-color: {self.cor}; border-radius: 1px;")
        layout.addWidget(separador)

        self.label_timer = QLabel(f"00:{self.tempo_total:02d}")
        self.label_timer.setStyleSheet(
            "font-size: 72px; font-weight: bold; color: #00ff88; "
            "background-color: #0a0a1a; padding: 15px; border-radius: 12px; "
            "border: 2px solid #00ff88;"
        )
        self.label_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_timer)

        layout.addSpacing(10)

        self.label_atual = QLabel("Turma Atual")
        self.label_atual.setStyleSheet("font-size: 22px; color: #888; background: transparent;")
        self.label_atual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_atual)

        self.label_turma_atual = QLabel("-")
        self.label_turma_atual.setStyleSheet(
            "font-size: 64px; font-weight: bold; color: white; "
            "background-color: #0a0a1a; padding: 10px; border-radius: 12px; "
            f"border: 3px solid {self.cor};"
        )
        self.label_turma_atual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_turma_atual)

        layout.addSpacing(5)

        self.label_proximo = QLabel("Proxima Turma")
        self.label_proximo.setStyleSheet("font-size: 20px; color: #888; background: transparent;")
        self.label_proximo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_proximo)

        self.label_turma_proximo = QLabel("-")
        self.label_turma_proximo.setStyleSheet(
            "font-size: 42px; font-weight: bold; color: #ccc; "
            "background-color: #0a0a1a; padding: 8px; border-radius: 10px; "
            "border: 1px solid #444;"
        )
        self.label_turma_proximo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_turma_proximo)

        layout.addSpacing(10)

        layout_btns = QHBoxLayout()
        layout_btns.setSpacing(10)

        self.btn_iniciar = QPushButton("INICIAR")
        self.btn_iniciar.setFixedHeight(50)
        self.btn_iniciar.setStyleSheet("font-size: 18px;")
        self.btn_iniciar.clicked.connect(self.iniciar_timer)
        layout_btns.addWidget(self.btn_iniciar)

        self.btn_parar = QPushButton("PARAR")
        self.btn_parar.setFixedHeight(50)
        self.btn_parar.setStyleSheet("font-size: 18px;")
        self.btn_parar.clicked.connect(self.parar_timer)
        layout_btns.addWidget(self.btn_parar)

        self.btn_chamar = QPushButton("CHAMAR")
        self.btn_chamar.setFixedHeight(50)
        self.btn_chamar.setStyleSheet("font-size: 18px;")
        self.btn_chamar.clicked.connect(self.chamar_turma)
        layout_btns.addWidget(self.btn_chamar)

        layout.addLayout(layout_btns)

        self.setLayout(layout)

        self.atualizar_proximo()

    def atualizar_proximo(self):
        if self.indice < len(self.turmas):
            self.label_turma_proximo.setText(self.turmas[self.indice])
        else:
            self.label_turma_proximo.setText("FIM")

    def iniciar_timer(self):
        if not self.timer_ativo:
            self.timer_ativo = True
            self.em_pausa = False
            self.tempo_restante = self.tempo_total
            self.atualizar_label_timer()
            self.timer_qt.start(1000)

    def parar_timer(self):
        self.timer_ativo = False
        self.em_pausa = False
        self.timer_qt.stop()

    def atualizar_timer(self):
        if self.em_pausa:
            self.tempo_restante -= 1
            if self.tempo_restante <= 0:
                self.em_pausa = False
                self.tempo_restante = self.tempo_total
                self.atualizar_label_timer()
                self.timer_qt.start(1000)
            else:
                self.atualizar_label_timer_pausa()
            return

        if self.timer_ativo and self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.atualizar_label_timer()
        else:
            self.chamar_turma()
            if self.indice < len(self.turmas):
                self.em_pausa = True
                self.tempo_restante = self.pausa_entre_chamadas
                self.atualizar_label_timer_pausa()
            else:
                self.parar_timer()

    def atualizar_label_timer_pausa(self):
        self.label_timer.setText(f"PAUSA: {self.tempo_restante}s")
        self.label_timer.setStyleSheet(
            "font-size: 72px; font-weight: bold; color: #ffaa00; "
            "background-color: #0a0a1a; padding: 15px; border-radius: 12px; "
            "border: 2px solid #ffaa00;"
        )

    def atualizar_label_timer(self):
        minutos = self.tempo_restante // 60
        segundos = self.tempo_restante % 60
        self.label_timer.setText(f"{minutos:02d}:{segundos:02d}")
        self.label_timer.setStyleSheet(
            "font-size: 72px; font-weight: bold; color: #00ff88; "
            "background-color: #0a0a1a; padding: 15px; border-radius: 12px; "
            "border: 2px solid #00ff88;"
        )

    def falar(self, texto):
        winsound.Beep(800, 200)
        try:
            engine = comtypes.client.CreateObject('SAPI.SpVoice')
            engine.Volume = 100
            engine.Rate = -1
            voices = engine.GetVoices()
            for v in voices:
                if 'pt' in v.Id.lower() or 'brazil' in v.Id.lower() or 'portuguese' in v.Id.lower():
                    engine.Voice = v
                    break
            engine.Speak(texto)
        except Exception:
            pass

    def chamar_turma(self):
        if self.indice < len(self.turmas):
            turma = self.turmas[self.indice]
            self.label_turma_atual.setText(turma)
            self.label_turma_atual.setStyleSheet(
                "font-size: 64px; font-weight: bold; color: #00ff88; "
                "background-color: #0a0a1a; padding: 10px; border-radius: 12px; "
                f"border: 3px solid {self.cor};"
            )
            num_fila = "1" if "primeiros" in self.nome_fila.lower() else "2"
            texto = f"{turma}, dirija-se a fila {num_fila}"
            threading.Thread(target=self.falar, args=(texto,), daemon=True).start()
            self.indice += 1
            self.atualizar_proximo()

    def resetar(self):
        self.parar_timer()
        self.indice = 0
        self.em_pausa = False
        self.label_turma_atual.setText("-")
        self.label_turma_atual.setStyleSheet(
            "font-size: 64px; font-weight: bold; color: white; "
            "background-color: #0a0a1a; padding: 10px; border-radius: 12px; "
            f"border: 3px solid {self.cor};"
        )
        self.atualizar_proximo()
        self.label_timer.setText(f"00:{self.tempo_total:02d}")
        self.label_timer.setStyleSheet(
            "font-size: 72px; font-weight: bold; color: #00ff88; "
            "background-color: #0a0a1a; padding: 15px; border-radius: 12px; "
            "border: 2px solid #00ff88;"
        )


class ConfigPanel(QWidget):
    def __init__(self, config, on_salvar, url_remoto=None, qr_b64=None):
        super().__init__()
        self.config = config
        self.on_salvar = on_salvar
        self.url_remoto = url_remoto
        self.qr_b64 = qr_b64
        self.dias = ["segunda", "terca", "quarta", "quinta", "sexta"]
        self.init_ui()

    def init_ui(self):
        self.lista_fila1 = None
        self.lista_fila2 = None
        self._indice_dia_atual = 0

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)

        titulo = QLabel("CONFIGURACOES")
        titulo.setStyleSheet("font-size: 36px; font-weight: bold; color: #e94560; background: transparent;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        separador = QLabel()
        separador.setFixedHeight(2)
        separador.setStyleSheet("background-color: #e94560;")
        layout.addWidget(separador)

        if self.url_remoto and self.qr_b64:
            sec_remoto = QLabel("CONTROLE REMOTO (CELULAR)")
            sec_remoto.setStyleSheet("font-size: 22px; font-weight: bold; color: #2ecc71; background: transparent;")
            layout.addWidget(sec_remoto)

            box_remoto = QFrame()
            box_remoto.setStyleSheet("background-color: #0a1a0a; border: 2px solid #2ecc71; border-radius: 10px;")
            box_layout = QHBoxLayout(box_remoto)
            box_layout.setSpacing(20)
            box_layout.setContentsMargins(20, 20, 20, 20)

            qr_bytes = QByteArray.fromBase64(self.qr_b64.encode())
            pixmap = QPixmap()
            pixmap.loadFromData(qr_bytes)
            pixmap = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_qr = QLabel()
            lbl_qr.setPixmap(pixmap)
            box_layout.addWidget(lbl_qr)

            lbl_info = QLabel()
            lbl_info.setText(
                f"Escaneie o QR code com a camera do celular\n"
                f"para abrir o controle remoto.\n\n"
                f"Endereço: {self.url_remoto}\n\n"
                f"Conexao: celular deve estar no mesmo WiFi do notebook."
            )
            lbl_info.setStyleSheet("font-size: 16px; color: #ccc; background: transparent;")
            box_layout.addWidget(lbl_info)

            layout.addWidget(box_remoto)

        sec_timer = QLabel("TEMPO DO TIMER")
        sec_timer.setStyleSheet("font-size: 22px; font-weight: bold; color: #4dabf7; background: transparent;")
        layout.addWidget(sec_timer)

        layout_timer = QHBoxLayout()
        layout_timer.setSpacing(15)

        lbl_seg = QLabel("Segundos:")
        lbl_seg.setStyleSheet("font-size: 18px; color: #ccc; background: transparent;")
        layout_timer.addWidget(lbl_seg)

        self.spin_timer = QSpinBox()
        self.spin_timer.setRange(5, 600)
        self.spin_timer.setValue(self.config["timer"]["segundos"])
        self.spin_timer.setSuffix(" s")
        self.spin_timer.setFixedWidth(150)
        layout_timer.addWidget(self.spin_timer)

        layout_timer.addStretch()
        layout.addLayout(layout_timer)

        sec_pausa = QLabel("PAUSA ENTRE CHAMADAS")
        sec_pausa.setStyleSheet("font-size: 22px; font-weight: bold; color: #4dabf7; background: transparent;")
        layout.addWidget(sec_pausa)

        layout_pausa = QHBoxLayout()
        layout_pausa.setSpacing(15)

        lbl_pausa = QLabel("Segundos:")
        lbl_pausa.setStyleSheet("font-size: 18px; color: #ccc; background: transparent;")
        layout_pausa.addWidget(lbl_pausa)

        self.spin_pausa = QSpinBox()
        self.spin_pausa.setRange(0, 60)
        self.spin_pausa.setValue(self.config["timer"].get("pausa_entre_chamadas", 5))
        self.spin_pausa.setSuffix(" s")
        self.spin_pausa.setFixedWidth(150)
        layout_pausa.addWidget(self.spin_pausa)

        layout_pausa.addStretch()
        layout.addLayout(layout_pausa)

        sec_dia = QLabel("DIA DA SEMANA")
        sec_dia.setStyleSheet("font-size: 22px; font-weight: bold; color: #4dabf7; background: transparent;")
        layout.addWidget(sec_dia)

        self.combo_dia = QComboBox()
        for dia in self.dias:
            self.combo_dia.addItem(dia.upper())
        self.combo_dia.setFixedWidth(200)
        self.combo_dia.currentIndexChanged.connect(self.carregar_dia)
        layout.addWidget(self.combo_dia)

        sec_fila1 = QLabel("FILA 1 - PRIMEIROS ANOS")
        sec_fila1.setStyleSheet("font-size: 22px; font-weight: bold; color: #4dabf7; background: transparent;")
        layout.addWidget(sec_fila1)

        self.lista_fila1 = QListWidget()
        self.lista_fila1.setMinimumHeight(150)
        layout.addWidget(self.lista_fila1)

        layout_add_fila1 = QHBoxLayout()
        layout_add_fila1.setSpacing(10)
        self.input_fila1 = QLineEdit()
        self.input_fila1.setPlaceholderText("Ex: 1D")
        self.input_fila1.setFixedWidth(200)
        layout_add_fila1.addWidget(self.input_fila1)

        btn_add_f1 = QPushButton("ADICIONAR")
        btn_add_f1.setFixedHeight(40)
        btn_add_f1.setStyleSheet("font-size: 14px; padding: 0 15px;")
        btn_add_f1.clicked.connect(self.adicionar_fila1)
        layout_add_fila1.addWidget(btn_add_f1)

        btn_rem_f1 = QPushButton("REMOVER")
        btn_rem_f1.setFixedHeight(40)
        btn_rem_f1.setStyleSheet("font-size: 14px; padding: 0 15px; background-color: #c0392b;")
        btn_rem_f1.clicked.connect(self.remover_fila1)
        layout_add_fila1.addWidget(btn_rem_f1)

        layout_add_fila1.addStretch()
        layout.addLayout(layout_add_fila1)

        sec_fila2 = QLabel("FILA 2 - SEGUNDOS E TERCEIROS ANOS")
        sec_fila2.setStyleSheet("font-size: 22px; font-weight: bold; color: #ff6b6b; background: transparent;")
        layout.addWidget(sec_fila2)

        self.lista_fila2 = QListWidget()
        self.lista_fila2.setMinimumHeight(150)
        layout.addWidget(self.lista_fila2)

        layout_add_fila2 = QHBoxLayout()
        layout_add_fila2.setSpacing(10)
        self.input_fila2 = QLineEdit()
        self.input_fila2.setPlaceholderText("Ex: 3D")
        self.input_fila2.setFixedWidth(200)
        layout_add_fila2.addWidget(self.input_fila2)

        btn_add_f2 = QPushButton("ADICIONAR")
        btn_add_f2.setFixedHeight(40)
        btn_add_f2.setStyleSheet("font-size: 14px; padding: 0 15px;")
        btn_add_f2.clicked.connect(self.adicionar_fila2)
        layout_add_fila2.addWidget(btn_add_f2)

        btn_rem_f2 = QPushButton("REMOVER")
        btn_rem_f2.setFixedHeight(40)
        btn_rem_f2.setStyleSheet("font-size: 14px; padding: 0 15px; background-color: #c0392b;")
        btn_rem_f2.clicked.connect(self.remover_fila2)
        layout_add_fila2.addWidget(btn_rem_f2)

        layout_add_fila2.addStretch()
        layout.addLayout(layout_add_fila2)

        layout.addSpacing(20)

        btn_salvar = QPushButton("SALVAR CONFIGURACOES")
        btn_salvar.setFixedHeight(60)
        btn_salvar.setStyleSheet("font-size: 20px; padding: 0 30px;")
        btn_salvar.clicked.connect(self.salvar)
        layout.addWidget(btn_salvar, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        self.carregar_dia()

    def _salvar_dia_atual(self):
        dia = self.dias[self._indice_dia_atual]
        self.config["turmas"][dia]["fila1"] = self._pegar_turmas_lista(self.lista_fila1)
        self.config["turmas"][dia]["fila2"] = self._pegar_turmas_lista(self.lista_fila2)

    def carregar_dia(self):
        if self.lista_fila1 is not None and self.lista_fila2 is not None:
            self._salvar_dia_atual()
        self._indice_dia_atual = self.combo_dia.currentIndex()
        dia = self.dias[self._indice_dia_atual]
        self.lista_fila1.clear()
        self.lista_fila2.clear()
        for t in self.config["turmas"][dia]["fila1"]:
            self.lista_fila1.addItem(QListWidgetItem(t))
        for t in self.config["turmas"][dia]["fila2"]:
            self.lista_fila2.addItem(QListWidgetItem(t))

    def _item_existe(self, lista, texto):
        for i in range(lista.count()):
            if lista.item(i).text() == texto:
                return True
        return False

    def adicionar_fila1(self):
        texto = self.input_fila1.text().strip().upper()
        if texto and not self._item_existe(self.lista_fila1, texto):
            self.lista_fila1.addItem(QListWidgetItem(texto))
            self.input_fila1.clear()

    def remover_fila1(self):
        item = self.lista_fila1.currentItem()
        if item:
            self.lista_fila1.takeItem(self.lista_fila1.row(item))

    def adicionar_fila2(self):
        texto = self.input_fila2.text().strip().upper()
        if texto and not self._item_existe(self.lista_fila2, texto):
            self.lista_fila2.addItem(QListWidgetItem(texto))
            self.input_fila2.clear()

    def remover_fila2(self):
        item = self.lista_fila2.currentItem()
        if item:
            self.lista_fila2.takeItem(self.lista_fila2.row(item))

    def _pegar_turmas_lista(self, lista):
        turmas = []
        for i in range(lista.count()):
            turmas.append(lista.item(i).text())
        return turmas

    def salvar(self):
        turmas_fila1 = self._pegar_turmas_lista(self.lista_fila1)
        turmas_fila2 = self._pegar_turmas_lista(self.lista_fila2)

        dia = self.dias[self._indice_dia_atual]
        self.config["turmas"][dia]["fila1"] = list(turmas_fila1)
        self.config["turmas"][dia]["fila2"] = list(turmas_fila2)

        self.config["timer"]["segundos"] = self.spin_timer.value()
        self.config["timer"]["pausa_entre_chamadas"] = self.spin_pausa.value()

        salvar_config(self.config)
        self.on_salvar()

        QMessageBox.information(self, "Sucesso", f"Configuracoes de {dia.upper()} salvas com sucesso!")


class FilaAlmoco(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = carregar_config()

        self.setWindowTitle("Sistema de Fila do Almoco")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()

        self.tempo_total = self.config["timer"]["segundos"]
        self.pausa_entre_chamadas = self.config["timer"].get("pausa_entre_chamadas", 5)
        self.dias = ["segunda", "terca", "quarta", "quinta", "sexta"]

        self.iniciar_servidor_remoto()

        self.init_ui()

    def iniciar_servidor_remoto(self):
        self.servidor = ServidorWeb(port=5000)
        self.url_remoto = self.servidor.iniciar()
        self.qr_b64 = gerar_qr_base64(self.url_remoto)

    def dia_atual(self):
        return self.dias[self.tabs.currentIndex()] if self.tabs.currentIndex() < 5 else self.dias[0]

    def init_ui(self):
        self.setStyleSheet(ESTILO_APP)

        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(5)
        layout_principal.setContentsMargins(15, 10, 15, 15)

        layout_header = QHBoxLayout()
        layout_header.setSpacing(20)

        titulo = QLabel("FILA DO ALMOCO")
        titulo.setStyleSheet("font-size: 42px; font-weight: bold; color: #e94560; background: transparent; letter-spacing: 3px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_header.addWidget(titulo)

        self.tabs = QTabBar()
        for dia in self.dias:
            self.tabs.addTab(dia.upper())
        self.tabs.addTab("CONFIGURACOES")
        self.tabs.setExpanding(True)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 14px 35px;
                font-size: 20px;
                font-weight: bold;
                margin-right: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QTabBar::tab:selected {
                background-color: #e94560;
                color: white;
            }
            QTabBar::tab:!selected {
                background-color: #16213e;
                color: #a0a0a0;
            }
        """)
        self.tabs.currentChanged.connect(self.mudar_aba)
        layout_header.addWidget(self.tabs, 2)

        layout_principal.addLayout(layout_header)

        separador = QLabel()
        separador.setFixedHeight(2)
        separador.setStyleSheet("background-color: #e94560;")
        layout_principal.addWidget(separador)

        self.stack = QStackedWidget()

        self.paginas_fila = []
        for dia in self.dias:
            turmas = self.config["turmas"][dia]
            pagina = QWidget()
            p_layout = QHBoxLayout(pagina)
            p_layout.setSpacing(20)
            f1 = FilaPanel("FILA 1 - PRIMEIROS ANOS", "#4dabf7", turmas["fila1"], self.tempo_total, self.pausa_entre_chamadas)
            f2 = FilaPanel("FILA 2 - SEGUNDOS E TERCEIROS ANOS", "#ff6b6b", turmas["fila2"], self.tempo_total, self.pausa_entre_chamadas)
            p_layout.addWidget(f1)
            p_layout.addWidget(f2)
            self.paginas_fila.append((f1, f2))
            self.stack.addWidget(pagina)

        self.config_panel = ConfigPanel(self.config, self.recarregar_config, self.url_remoto, self.qr_b64)
        self.stack.addWidget(self.config_panel)

        layout_principal.addWidget(self.stack)

        central.setLayout(layout_principal)

        self.tabs.setCurrentIndex(0)

        dia_atual_holder.clear()
        dia_atual_holder.append(self.dia_atual)
        filas_ref["fila1"] = self.paginas_fila[0][0]
        filas_ref["fila2"] = self.paginas_fila[0][1]

    def mudar_aba(self, index):
        self.stack.setCurrentIndex(index)
        if index < 5:
            f1, f2 = self.paginas_fila[index]
            filas_ref["fila1"] = f1
            filas_ref["fila2"] = f2

    def recarregar_config(self):
        self.config = carregar_config()
        self.tempo_total = self.config["timer"]["segundos"]
        self.pausa_entre_chamadas = self.config["timer"].get("pausa_entre_chamadas", 5)

        for i, dia in enumerate(self.dias):
            turmas = self.config["turmas"][dia]
            f1, f2 = self.paginas_fila[i]
            f1.resetar()
            f2.resetar()
            f1.tempo_total = self.tempo_total
            f1.pausa_entre_chamadas = self.pausa_entre_chamadas
            f1.turmas = turmas["fila1"]
            f1.atualizar_proximo()
            f2.tempo_total = self.tempo_total
            f2.pausa_entre_chamadas = self.pausa_entre_chamadas
            f2.turmas = turmas["fila2"]
            f2.atualizar_proximo()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = FilaAlmoco()
    janela.show()
    sys.exit(app.exec())
