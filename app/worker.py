# bibliotecas
from PySide6.QtCore import QObject, Signal, Slot

from lumen_core import LumenError, convert_zip


class ConversionWorker(QObject):
    progress_changed = Signal(int, int, str)
    log_message = Signal(str, str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, input_zip, output_dir):
        super().__init__()
        self.input_zip = input_zip
        self.output_dir = output_dir

    def handle_progress(self, event):
        current = event["current"]
        total = event["total"]
        file_name = event["file"]
        self.progress_changed.emit(current, total, file_name)

    def handle_log(self, level, message):
        self.log_message.emit(level, message)

    @Slot()
    def run(self):
        try:
            result = convert_zip(
                self.input_zip,
                output_dir=self.output_dir,
                progress_callback=self.handle_progress,
                log_callback=self.handle_log,
            )
            self.finished.emit(result)
        except LumenError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(f"Unexpected error: {exc}")
