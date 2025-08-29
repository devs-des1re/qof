"""Module docstring"""
import os
from pathlib import Path
import shutil
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QStyledItemDelegate,
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPen
from PySide6.QtCore import Qt, QSettings, QStandardPaths

from darkdetect import isDark



class MainWindow(QMainWindow):
    """Main window class"""
    def __init__(self):
        super().__init__()
        self.resources_path = Path(__file__).parent / "resources"
        self.width = 400
        self.height = 400
        self.setWindowTitle("qof")
        self.setGeometry(0, 0, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setWindowIcon(QPixmap(self.resources_path / "icon.ico"))
        self.folder_path = None
        self._init__ui()
        self.__init__settings()
        self.__init__console()

    def _init__ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        ### Select Folder ###
        self.folder_layout = QHBoxLayout()
        self.main_layout.addLayout(self.folder_layout)

        self.folder_location = QLineEdit()
        self.folder_location.setReadOnly(True)
        self.folder_location.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.folder_layout.addWidget(self.folder_location)

        self.select_folder = QPushButton("Select Folder")
        self.select_folder.clicked.connect(self.on_select_folder_button_clicked)
        self.folder_layout.addWidget(self.select_folder)

        ### Folder Table ###
        self.folders_table = QTableWidget(0, 3)
        self.folders_table.setHorizontalHeaderLabels(["Folder", "Extension", "Enabled"])
        self.folders_table.setItemDelegate(CustomDelegate(self.folders_table))
        self.folders_table.itemChanged.connect(self.on_item_changed)

        self.horizontal_header = self.folders_table.horizontalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.Stretch)

        self.vertical_header = self.folders_table.verticalHeader()
        self.vertical_header.setVisible(False)

        self.main_layout.addWidget(self.folders_table)

        ### Main Buttons ###
        self.buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.buttons_layout)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.on_add_button_clicked)
        self.buttons_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.on_remove_button_clicked)
        self.buttons_layout.addWidget(self.remove_button)

        self.organize_button = QPushButton("Organize")
        self.organize_button.clicked.connect(self.on_organize_button_clicked)
        self.buttons_layout.addWidget(self.organize_button)

        ### Set Stylesheet ###
        self.set_stylesheet()

    def __init__settings(self):
        self.settings = QSettings("qof", "Core")

        try:
            self.move(self.settings.value("Window Position"))
            self.folder_location.setText(self.settings.value("Folder Location"))
            self.folder_path = self.settings.value("Folder Location")
            self.list_to_table(self.settings.value("Table Data"))
        except Exception as e:
            print('error', e)
            self.folder_path = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation
            )

    def __init__console(self):
        self.console = ConsoleWindow()
        self.console.hide()

        sys.stdout = self.console
        sys.stderr = self.console

        print("Console Initalized...")

    ### Button Connections ###
    def on_select_folder_button_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder", self.folder_path
        )

        if folder_path:
            self.folder_location.setText(folder_path)
            self.folder_path = folder_path

    def on_add_button_clicked(self):
        row = self.folders_table.rowCount()
        self.folders_table.insertRow(row)

        ### First Two Columns ###
        for col in range(2):
            item = QTableWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.folders_table.setItem(row, col, item)

        ### Checkbox ###
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
        )
        checkbox_item.setCheckState(Qt.CheckState.Checked)
        self.folders_table.setItem(row, 2, checkbox_item)

        self.folders_table.setRowHeight(row, 39)

    def on_remove_button_clicked(self):
        row = self.folders_table.currentRow()
        if row != -1:
            self.folders_table.removeRow(row)
        else:
            self.create_message(
                QMessageBox.Icon.Warning, "Please select a row to remove."
            )

    def on_organize_button_clicked(self):
        if self.folder_location.text() == "":
            self.create_message(
                QMessageBox.Icon.Warning, "A folder location hasn't been selected."
            )
            return

        row_count = self.folders_table.rowCount()

        for row in range(row_count):
            folder_name = self.folders_table.item(row, 0).text().strip()
            extension_name = self.folders_table.item(row, 1).text().strip()

            enabled = self.folders_table.item(row, 2)
            enabled = enabled.checkState()

            if enabled == Qt.CheckState.Checked:
                if folder_name != "" and extension_name != "":
                    try:
                        folder_path = f"{self.folder_location.text()}/{folder_name}"
                        os.makedirs(folder_path, exist_ok=True)
                        print(
                            "-----------------------------------------------------------------"
                        )
                        print(f"Success: Folder created '{folder_path}'")
                    except Exception as error:
                        print(
                            "-----------------------------------------------------------------"
                        )
                        print(f"Error: {error}")
                        self.create_message(
                            QMessageBox.Icon.Warning,
                            "An error has occured while creating the folder.",
                        )
                        return

                    try:
                        for filename in os.listdir(self.folder_location.text()):
                            file_path = os.path.join(
                                self.folder_location.text(), filename
                            )

                            if os.path.isfile(file_path) and filename.endswith(
                                f".{extension_name.lower()}"
                            ):
                                shutil.move(file_path, folder_path)
                                print(
                                    "-----------------------------------------------"
                                    "------------------"
                                )
                                print(
                                    f"Success: Moved '{file_path}' to '{folder_path}'"
                                )
                    except Exception as error:
                        print(
                            "-----------------------------------------------------------------"
                        )
                        print(f"Error: {error}")
                        self.create_message(
                            QMessageBox.Icon.Warning,
                            "An error has occured while moving a file.",
                        )
                        return

        self.create_message(
            QMessageBox.Icon.Information, "Your files have been successfully organized!"
        )

    ### Item Changed ###
    def on_item_changed(self, item):
        if item.column() == 2:
            if item.checkState() == Qt.Checked:
                item.setText("Enabled")
            else:
                item.setText("Disabled")

    ### Quick Functions ###
    def create_message(self, icon, text):
        message_box = QMessageBox(self)
        message_box.setWindowTitle("qof")
        message_box.setText(text)
        message_box.setIcon(icon)

        message_box.exec()

    def table_to_list(self):
        rows = self.folders_table.rowCount()
        cols = self.folders_table.columnCount()
        data = []

        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.folders_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def list_to_table(self, data):
        if data != []:
            self.folders_table.setRowCount(len(data))
            self.folders_table.setColumnCount(len(data[0]) if data else 0)

            for row, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    if col == 2:
                        item = QTableWidgetItem()
                        item.setFlags(
                            Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
                        )

                        if str(value) == "Enabled":
                            item.setCheckState(Qt.CheckState.Checked)
                        else:
                            item.setCheckState(Qt.CheckState.Unchecked)

                        self.folders_table.setItem(row, col, item)
                        self.folders_table.setRowHeight(row, 39)
                    else:
                        self.folders_table.setItem(
                            row, col, QTableWidgetItem(str(value))
                        )
                        self.folders_table.setRowHeight(row, 39)

    ### Set Stylesheet ###
    def set_stylesheet(self):
        with open(
            f"{str(self.resources_path)}\\stylesheets\\{'dark' if isDark() else 'light'}.txt",
            encoding='utf-8',
        ) as file:
            style = file.read()
            self.setStyleSheet(style)

    ### Events ###
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F9:
            self.console.setVisible(not self.console.isVisible())

    def closeEvent(self, event):
        self.settings.setValue("Window Position", self.pos())
        self.settings.setValue("Folder Location", self.folder_location.text())
        self.settings.setValue("Table Data", self.table_to_list())
        print(self.table_to_list())
        return super().closeEvent(event)

        return super().closeEvent(event)

class ConsoleWindow(QTextEdit):
    def __init__(self):
        super().__init__()
        self.resources_path = Path(__file__).parent / "resources"
        self.setWindowTitle("Debugger")
        self.setGeometry(0, 0, 400, 400)
        self.setWindowIcon(QPixmap(self.resources_path / "Icon.ico"))
        self._buffer = ""

        self._init__ui()

    def _init__ui(self):
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setReadOnly(True)
        self.font = QFont("Monospace", 10)
        self.setFont(self.font)

        self.setStyleSheet(
            """
            QTextEdit {
                background-color: transparent;
                font: Roboto;
            }
        """
        )

    def write(self, text):
        self._buffer += text
        lines = self._buffer.split("\n")
        for line in lines[:-1]:
            if line.strip():
                self.insertPlainText(line + "\n")
        self._buffer = lines[-1]

    def flush(self):
        if self._buffer.strip():
            self.insertPlainText(self._buffer + "\n")
        self._buffer = ""


class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        painter.save()
        try:
            grid_color = self.get_color()
            pen = QPen(grid_color)
            pen.setWidth(1)
            painter.setPen(pen)

            rect = option.rect

            if index.column() in [0, 1]:
                painter.drawLine(rect.topRight(), rect.bottomRight())

            total_rows = index.model().rowCount()

            if index.row() < total_rows - 1:
                painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        finally:
            painter.restore()

    @staticmethod
    def get_color():
        if isDark():
            return QColor(255, 255, 255)
        return QColor(85, 85, 85)


# Main
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("qof")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
