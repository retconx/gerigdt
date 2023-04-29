import configparser, os, re
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
)

reLizenzcode = "^([A-F0-9]{5}-){4}[A-F0-9]{5}$"

class EinstellungenProgrammerweiterungen(QDialog):
    def __init__(self, configPath):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.lanr = configIni["Erweiterungen"]["lanr"]
        self.lizenzcode = configIni["Erweiterungen"]["lizenzcode"]

        self.setWindowTitle("Einstellungen für Programmerweiterungen (Add-ons)")
        self.setMinimumWidth(460)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept) # type:ignore
        self.buttonBox.rejected.connect(self.reject) # type:ignore

        dialogLayoutV = QVBoxLayout()
        # Groupbox LANR
        groupboxLayoutLanr = QVBoxLayout()
        groupboxLanr = QGroupBox("LANR (9 Ziffern)")
        groupboxLanr.setStyleSheet("font-weight:bold")
        self.lineEditLanr = QLineEdit(self.lanr)
        self.lineEditLanr.setStyleSheet("font-weight:normal")
        groupboxLayoutLanr.addWidget(self.lineEditLanr)
        groupboxLanr.setLayout(groupboxLayoutLanr)
        # Groupbox Lizenzcode
        groupboxLayoutLizenzcode = QVBoxLayout()
        groupboxLizenzcode = QGroupBox("Lizenzcode")
        groupboxLizenzcode.setStyleSheet("font-weight:bold")
        self.lineEditLizenzcode = QLineEdit(self.lizenzcode)
        self.lineEditLizenzcode.setStyleSheet("font-weight:normal")
        groupboxLayoutLizenzcode.addWidget(self.lineEditLizenzcode)
        groupboxLizenzcode.setLayout(groupboxLayoutLizenzcode)
        dialogLayoutV.addWidget(groupboxLanr)
        dialogLayoutV.addWidget(groupboxLizenzcode)
        dialogLayoutV.addWidget(self.buttonBox)
        dialogLayoutV.setContentsMargins(10, 10, 10, 10)
        dialogLayoutV.setSpacing(20)
        self.setLayout(dialogLayoutV)
        self.lineEditLanr.setFocus()
        self.lineEditLanr.selectAll()

    def accept(self):
        if len(self.lineEditLanr.text()) != 9:
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Die LANR ist ungültig.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditLanr.setFocus()
            self.lineEditLanr.selectAll()
        elif not re.match(reLizenzcode, self.lineEditLizenzcode.text()):
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Der Lizenzcode ist ungültig.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditLizenzcode.setFocus()
            self.lineEditLizenzcode.selectAll()
        else:
            self.done(1)