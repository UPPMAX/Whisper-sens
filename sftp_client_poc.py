import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QMessageBox, QTreeView, QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import paramiko

class SFTPClient(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SFTP Client')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel('Username:', self)
        layout.addWidget(self.username_label)
        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Password:', self)
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.upload_button = QPushButton('Upload File', self)
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)

        self.download_button = QPushButton('Download File', self)
        self.download_button.clicked.connect(self.download_file)
        layout.addWidget(self.download_button)

        self.browse_button = QPushButton('Browse Remote Directory', self)
        self.browse_button.clicked.connect(self.browse_remote_directory)
        layout.addWidget(self.browse_button)

        self.setLayout(layout)

    def connect_sftp(self):
        try:
            self.transport = paramiko.Transport(('bianca-sftp.uppmax.uu.se', 22))
            self.transport.connect(username=self.username_input.text(), password=self.password_input.text())
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        except Exception as e:
            QMessageBox.critical(self, 'Connection Error', str(e))
            return False
        return True

    def upload_file(self):
        if not self.connect_sftp():
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload", "", "All Files (*)", options=options)
        if file_path:
            try:
                remote_path = QFileDialog.getSaveFileName(self, "Save As", "", "All Files (*)")[0]
                if remote_path:
                    self.sftp.put(file_path, remote_path)
                    QMessageBox.information(self, 'Success', 'File uploaded successfully')
            except Exception as e:
                QMessageBox.critical(self, 'Upload Error', str(e))
        self.sftp.close()
        self.transport.close()

    def download_file(self):
        if not self.connect_sftp():
            return

        remote_path, _ = QFileDialog.getOpenFileName(self, "Select File to Download", "", "All Files (*)")
        if remote_path:
            try:
                local_path = QFileDialog.getSaveFileName(self, "Save As", "", "All Files (*)")[0]
                if local_path:
                    self.sftp.get(remote_path, local_path)
                    QMessageBox.information(self, 'Success', 'File downloaded successfully')
            except Exception as e:
                QMessageBox.critical(self, 'Download Error', str(e))
        self.sftp.close()
        self.transport.close()

    def browse_remote_directory(self):
        if not self.connect_sftp():
            return

        dialog = QDialog(self)
        dialog.setWindowTitle('Remote Directory Structure')
        dialog.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout(dialog)
        tree_view = QTreeView(dialog)
        layout.addWidget(tree_view)

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Name'])
        root_node = model.invisibleRootItem()

        self.populate_model(root_node, '.')
        tree_view.setModel(model)

        dialog.exec_()

        self.sftp.close()
        self.transport.close()

    def populate_model(self, parent, path):
        for item in self.sftp.listdir_attr(path):
            item_name = item.filename
            item_path = f"{path}/{item_name}"
            item_node = QStandardItem(item_name)
            parent.appendRow(item_node)
            if paramiko.S_ISDIR(item.st_mode):
                self.populate_model(item_node, item_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = SFTPClient()
    client.show()
    sys.exit(app.exec_())