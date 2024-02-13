import configparser, os, sys, gdttoolsL, datetime, logger
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QCheckBox,
    QFileDialog,
    QRadioButton,
    QMessageBox
)

class EinstellungenImportExport(QDialog):
    def __init__(self, configPath):
        super().__init__()
        self.setFixedWidth(340)
        self.configPath = configPath

        #config.ini lesen
        self.configIni = configparser.ConfigParser()
        self.configIni.read(os.path.join(configPath, "config.ini"))

        self.setWindowTitle("Einstellungen im-/ exportieren")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Importieren...")
        self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        self.buttonBox.accepted.connect(self.accept) # type: ignore
        self.buttonBox.rejected.connect(self.reject) # type: ignore

        # Prüfen, ob Lizenzschlüssel verschlüsselt in config.ini
        lizenzschluessel = self.configIni["Erweiterungen"]["lizenzschluessel"]
        if len(lizenzschluessel) != 29:
            lizenzschluessel = gdttoolsL.GdtToolsLizenzschluessel.dekrypt(lizenzschluessel)

        mainLayoutV = QVBoxLayout()
        
        # Groupbox Import/Export
        groupboxImportExport = QGroupBox("Import/Export")
        groupboxImportExport.setStyleSheet("font-weight:bold")
        self.radiobuttonImport = QRadioButton()
        self.radiobuttonImport.setText("Importieren")
        self.radiobuttonImport.setStyleSheet("font-weight:normal")
        self.radiobuttonImport.setChecked(True)
        self.radiobuttonImport.clicked.connect(self.radiobuttonClicked) # type: ignore
        self.radiobuttonExport = QRadioButton()
        self.radiobuttonExport.setText("Exportieren")
        self.radiobuttonExport.setStyleSheet("font-weight:normal")
        self.radiobuttonExport.clicked.connect(self.radiobuttonClicked) # type: ignore
        groupboxImportExportLayout = QVBoxLayout()
        groupboxImportExportLayout.addWidget(self.radiobuttonImport)
        groupboxImportExportLayout.addWidget(self.radiobuttonExport)
        groupboxImportExport.setLayout(groupboxImportExportLayout)

        # Groupbox Einstellungen
        self.checkboxTextListe = ["Allgemeine Einstellungen", "GDT-Einstellungen", "BenutzerInnen", "LANR/Lizenzschlüssel"]
        self.checkboxEinstellungen = []
        self.groupboxEinstellungen = QGroupBox("Zu exportierende Einstellungen")
        self.groupboxEinstellungen.setStyleSheet("font-weight:bold")
        for text in self.checkboxTextListe:
            tempCheckbox = QCheckBox(text)
            tempCheckbox.setStyleSheet("font-weight:normal")
            tempCheckbox.setChecked(True)
            tempCheckbox.clicked.connect(self.checkboxClicked) # type: ignore
            self.checkboxEinstellungen.append(tempCheckbox)
        groupboxEinstellungenLayout = QVBoxLayout()
        for cb in self.checkboxEinstellungen:
            groupboxEinstellungenLayout.addWidget(cb)
        self.groupboxEinstellungen.setLayout(groupboxEinstellungenLayout)
        
        mainLayoutV.addWidget(groupboxImportExport)
        mainLayoutV.addWidget(self.groupboxEinstellungen)
        mainLayoutV.addWidget(self.buttonBox)
        self.setLayout(mainLayoutV)
        self.radiobuttonClicked()

    def radiobuttonClicked(self):
        if self.radiobuttonImport.isChecked():
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Importieren...")
            self.groupboxEinstellungen.setTitle("Zu importierende Einstellungen")
            
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText("Exportieren...")
            self.groupboxEinstellungen.setTitle("Zu exportierende Einstellungen")

    def checkboxClicked(self):
        gecheckt = 0
        for cb in self.checkboxEinstellungen:
            if cb.isChecked():
                gecheckt += 1
        if gecheckt == 0:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    def accept(self):
        if self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).text() == "Importieren...":
            fd = QFileDialog(self)
            fd.setFileMode(QFileDialog.FileMode.ExistingFile)
            fd.setWindowTitle("Einstellungen importieren")
            fd.setModal(True)
            fd.setNameFilters(["GeriGDT-Einstellungsdateien (*.ged)"])
            fd.setLabelText(QFileDialog.DialogLabel.Accept, "Laden")
            fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
            if fd.exec() == 1:
                datei = fd.selectedFiles()[0]
                configImport = configparser.ConfigParser()
                configImport.read(datei)
                if "Allgemein" in configImport.sections() or "GDT" in configImport.sections() or "Benutzer" in configImport.sections() or "Erweiterungen" in configImport.sections():
                    i=0
                    for section in configImport.sections():
                        if self.checkboxEinstellungen[i].isChecked():
                            for option in configImport.options(section):
                                self.configIni[section][option] = configImport.get(section, option)
                        i += 1
                    try:
                        with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                            self.configIni.write(configfile)
                        self.done(1)
                        mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Die Einstellungen wurden erfolgreich importiert. Damit diese wirksam werden, muss GeriGDT neu gestartet werden.\nSoll GeriGDT neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                        mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                        mb.button(QMessageBox.StandardButton.No).setText("Nein")
                        if mb.exec() == QMessageBox.StandardButton.Yes:
                            os.execl(sys.executable, __file__, *sys.argv)
                    except Exception as e:
                        mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Fehler beim Importieren der Einstellungen: " + str(e), QMessageBox.StandardButton.Ok)
                        mb.exec()
                else:
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Die Datei " + datei + " ist keine gültige GeriGDT-Konfigurationsdatei", QMessageBox.StandardButton.Ok)
                    mb.exec()
        else:
            fd = QFileDialog(self)
            fd.setFileMode(QFileDialog.FileMode.Directory)
            fd.setWindowTitle("Einstellungen exportieren")
            fd.setModal(True)
            fd.setLabelText(QFileDialog.DialogLabel.Accept, "Speichern")
            fd.setLabelText(QFileDialog.DialogLabel.Reject, "Abbrechen")
            if fd.exec() == 1:
                configExport = configparser.ConfigParser()
                pfad = fd.directory().absolutePath()
                dateiname = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M%S") + "_GeriGdtEinstellungen.ged"
                datei = os.path.join(pfad, dateiname)
                try:
                    with open(datei, "w") as exportfile:
                        if self.checkboxEinstellungen[0].isChecked():
                            section = "Allgemein"
                            configExport.add_section(section)
                            for option in self.configIni.options(section):
                                configExport[section][option] = self.configIni[section][option]
                        if self.checkboxEinstellungen[1].isChecked():
                            section = "GDT"
                            configExport.add_section(section)
                            for option in self.configIni.options(section):
                                configExport[section][option] = self.configIni[section][option]
                        if self.checkboxEinstellungen[2].isChecked():
                            section = "Benutzer"
                            configExport.add_section(section)
                            for option in self.configIni.options(section):
                                configExport[section][option] = self.configIni[section][option]
                        if self.checkboxEinstellungen[3].isChecked():
                            section = "Erweiterungen"
                            configExport.add_section(section)
                            for option in self.configIni.options(section):
                                configExport[section][option] = self.configIni[section][option]
                        configExport.write(exportfile)
                        mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Die gewünschten Einstellungen wurden erfolgreich unter dem Namen " + dateiname + " exportiert.", QMessageBox.StandardButton.Ok)
                        mb.exec()
                        self.done(1)
                except Exception as e:
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Fehler beim Exportieren der Einstellungen: " + str(e), QMessageBox.StandardButton.Ok)
                    mb.exec()
                            
