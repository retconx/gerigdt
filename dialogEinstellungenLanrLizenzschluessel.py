import configparser, os, re
import gdttoolsL
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
)

reLanr = "^\\d{9}$"
reLizenzschluessel = "^([A-Z0-9]{5}-){4}[A-F0-9]{5}$"

class EinstellungenProgrammerweiterungen(QDialog):
    def __init__(self, configPath):
        super().__init__()

        #config.ini lesen
        configIni = configparser.ConfigParser()
        configIni.read(os.path.join(configPath, "config.ini"))
        self.lanr = configIni["Erweiterungen"]["lanr"]
        self.lizenzschluessel = configIni["Erweiterungen"]["lizenzschluessel"]

        self.setWindowTitle("LANR und Lizenzschlüssel")
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
        # Groupbox Lizenzschlüssel
        groupboxLayoutLizenzschluessel = QVBoxLayout()
        groupboxLizenzschluessel = QGroupBox("Lizenzschluessel")
        groupboxLizenzschluessel.setStyleSheet("font-weight:bold")
        self.lineEditLizenzschluessel = QLineEdit(self.lizenzschluessel)
        self.lineEditLizenzschluessel.setStyleSheet("font-weight:normal")
        groupboxLayoutLizenzschluessel.addWidget(self.lineEditLizenzschluessel)
        groupboxLizenzschluessel.setLayout(groupboxLayoutLizenzschluessel)
        dialogLayoutV.addWidget(groupboxLanr)
        dialogLayoutV.addWidget(groupboxLizenzschluessel)
        dialogLayoutV.addWidget(self.buttonBox)
        dialogLayoutV.setContentsMargins(10, 10, 10, 10)
        dialogLayoutV.setSpacing(20)
        self.setLayout(dialogLayoutV)
        self.lineEditLanr.setFocus()
        self.lineEditLanr.selectAll()

    def accept(self):
        if not re.match(reLanr, self.lineEditLanr.text()) or not gdttoolsL.GdtToolsLizenzschluessel.checksummeLanrKorrekt(self.lineEditLanr.text()):
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Die LANR ist ungültig.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditLanr.setFocus()
            self.lineEditLanr.selectAll()
        elif not re.match(reLizenzschluessel, self.lineEditLizenzschluessel.text()) or not gdttoolsL.GdtToolsLizenzschluessel.lanrGueltig(self.lineEditLanr.text(), self.lineEditLizenzschluessel.text()):
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis", "Die LANR/lizenzschluessel-Kombination ist ungültig.", QMessageBox.StandardButton.Ok)
            mb.exec()
            self.lineEditLizenzschluessel.setFocus()
            self.lineEditLizenzschluessel.selectAll()
        else:
            self.done(1)