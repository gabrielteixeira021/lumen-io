import os
import shutil
import subprocess
import sys

from PySide6.QtCore import QThread, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.worker import ConversionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.last_output_dir = ""
        self.setWindowTitle("Lúmen Converter")
        self.resize(760, 520)
        self.build_ui()
        self.update_convert_button_state()

    def build_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        input_label = QLabel("Arquivo ZIP de entrada")
        input_row = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Selecione um arquivo .zip")
        self.input_edit.textChanged.connect(self.update_convert_button_state)
        input_button = QPushButton("Selecionar ZIP")
        input_button.clicked.connect(self.select_input_zip)
        input_row.addWidget(self.input_edit)
        input_row.addWidget(input_button)

        output_label = QLabel("Pasta de saida")
        output_row = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Selecione a pasta de saida")
        self.output_edit.setText(os.path.abspath("lumen_output"))
        self.output_edit.textChanged.connect(self.update_convert_button_state)
        output_button = QPushButton("Escolher pasta")
        output_button.clicked.connect(self.select_output_dir)
        output_row.addWidget(self.output_edit)
        output_row.addWidget(output_button)

        progress_label = QLabel("Progresso")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)

        self.status_label = QLabel("Selecione um ZIP para iniciar.")

        log_label = QLabel("Log")
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)

        actions_row = QHBoxLayout()
        self.convert_button = QPushButton("Converter")
        self.convert_button.clicked.connect(self.start_conversion)
        self.open_output_button = QPushButton("Abrir pasta de saida")
        self.open_output_button.clicked.connect(self.open_output_dir)
        self.open_output_button.setEnabled(False)
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)

        actions_row.addWidget(self.convert_button)
        actions_row.addWidget(self.open_output_button)
        actions_row.addWidget(self.close_button)

        main_layout.addWidget(input_label)
        main_layout.addLayout(input_row)
        main_layout.addWidget(output_label)
        main_layout.addLayout(output_row)
        main_layout.addWidget(progress_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_output)
        main_layout.addLayout(actions_row)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def append_log(self, level, message):
        self.log_output.appendPlainText(f"[{level.upper()}] {message}")

    def update_convert_button_state(self):
        has_input = bool(self.input_edit.text().strip())
        has_output = bool(self.output_edit.text().strip())
        is_running = self.thread is not None and self.thread.isRunning()
        self.convert_button.setEnabled(has_input and has_output and not is_running)

    def select_input_zip(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione o arquivo ZIP",
            "",
            "Arquivos ZIP (*.zip)",
        )
        if file_path:
            self.input_edit.setText(file_path)

    def select_output_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta de saida",
            self.output_edit.text() or os.getcwd(),
        )
        if folder:
            self.output_edit.setText(folder)

    def set_ui_running_state(self, running):
        self.input_edit.setEnabled(not running)
        self.output_edit.setEnabled(not running)
        self.open_output_button.setEnabled(not running and bool(self.last_output_dir))
        self.close_button.setEnabled(not running)
        self.update_convert_button_state()

    def start_conversion(self):
        input_zip = self.input_edit.text().strip()
        output_dir = self.output_edit.text().strip()

        if not input_zip:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo ZIP.")
            return

        if not output_dir:
            QMessageBox.warning(self, "Aviso", "Selecione uma pasta de saida.")
            return

        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparando conversao...")
        self.append_log("info", f"Input: {input_zip}")
        self.append_log("info", f"Output: {output_dir}")

        self.thread = QThread()
        self.worker = ConversionWorker(input_zip, output_dir)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_changed.connect(self.on_progress_changed)
        self.worker.log_message.connect(self.append_log)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_thread)

        self.set_ui_running_state(True)
        self.thread.start()

    def on_progress_changed(self, current, total, file_name):
        self.progress_bar.setMaximum(total if total > 0 else 1)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Convertendo {current}/{total}: {file_name}")

    def on_conversion_finished(self, result):
        self.last_output_dir = os.path.abspath(result["output_dir"])
        self.status_label.setText(
            f"Concluido: {result['converted']} convertido(s), {result['failed']} falha(s)"
        )
        self.append_log("info", "Conversao finalizada.")
        self.open_output_button.setEnabled(True)

        if result["failed"] > 0:
            QMessageBox.warning(
                self,
                "Conversao concluida com avisos",
                f"{result['failed']} arquivo(s) falharam.",
            )
        else:
            QMessageBox.information(
                self,
                "Sucesso",
                "Conversao concluida com sucesso.",
            )

    def on_conversion_error(self, message):
        self.status_label.setText("Erro durante a conversao.")
        self.append_log("error", message)
        QMessageBox.critical(self, "Erro", message)

    def cleanup_thread(self):
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

        if self.thread is not None:
            self.thread.deleteLater()
            self.thread = None

        self.set_ui_running_state(False)

    def open_output_dir(self):
        output_dir = self.last_output_dir or self.output_edit.text().strip()
        output_dir = os.path.abspath(output_dir) if output_dir else ""

        if not output_dir or not os.path.exists(output_dir):
            QMessageBox.warning(self, "Aviso", "A pasta de saida nao existe.")
            return

        if not os.path.isdir(output_dir):
            QMessageBox.warning(self, "Aviso", "O caminho de saida nao e uma pasta.")
            return

        errors = []

        if sys.platform.startswith("linux"):
            desktop = (os.environ.get("XDG_CURRENT_DESKTOP") or "").upper()
            commands = []

            if "KDE" in desktop:
                commands.extend(
                    [
                        ["dolphin", output_dir],
                        ["kioclient5", "exec", output_dir],
                        ["kioclient", "exec", output_dir],
                    ]
                )

            commands.extend(
                [
                    ["xdg-open", output_dir],
                    ["gio", "open", output_dir],
                ]
            )

            launch_env = os.environ.copy()

            # PyInstaller bundles often inject library/plugin paths that break
            # external desktop apps like Dolphin/KIO when launched as children.
            original_ld_library_path = launch_env.get("LD_LIBRARY_PATH_ORIG")
            if original_ld_library_path is not None:
                launch_env["LD_LIBRARY_PATH"] = original_ld_library_path
            else:
                launch_env.pop("LD_LIBRARY_PATH", None)

            for variable_name in (
                "PYTHONHOME",
                "PYTHONPATH",
                "PYTHONEXECUTABLE",
                "QT_PLUGIN_PATH",
                "QML2_IMPORT_PATH",
            ):
                launch_env.pop(variable_name, None)

            for command in commands:
                executable = shutil.which(command[0])
                if executable is None:
                    errors.append(f"Comando nao encontrado: {command[0]}")
                    continue

                try:
                    subprocess.Popen(
                        [executable, *command[1:]],
                        env=launch_env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True,
                    )
                    return
                except OSError as exc:
                    errors.append(f"{' '.join(command)}: {exc}")
        elif sys.platform == "darwin":
            try:
                subprocess.Popen(
                    ["open", output_dir],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return
            except OSError as exc:
                errors.append(f"open: {exc}")
        elif sys.platform.startswith("win"):
            try:
                os.startfile(output_dir)
                return
            except OSError as exc:
                errors.append(str(exc))
        else:
            if QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir)):
                return
            errors.append("QDesktopServices.openUrl falhou")

        error_details = "\n".join(errors) if errors else "sem detalhes"
        QMessageBox.critical(
            self,
            "Erro",
            f"Nao foi possivel abrir a pasta de saida:\n{output_dir}\n\n{error_details}",
        )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
