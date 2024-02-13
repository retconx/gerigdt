import sys, configparser, os, datetime, shutil,logger
import gdt, gdtzeile, gdttoolsL
import dialogUeberGeriGdt, dialogEinstellungenGdt, dialogEinstellungenBenutzer, dialogEinstellungenAllgemein, dialogEinstellungenLanrLizenzschluessel, dialogEinstellungenImportExport, dialogEula
import geriasspdf
from PySide6.QtCore import Qt, QSize, QDate, QTime, QTranslator, QLibraryInfo, QEvent
from PySide6.QtGui import QFont, QAction, QKeySequence, QIcon, QDesktopServices, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QRadioButton,
    QWidget,
    QLabel, 
    QDateEdit,
    QComboBox,
    QMessageBox, 
    QCheckBox
)
import requests

basedir = os.path.dirname(__file__)
# Gegebenenfalls pdf- und log-Verzeichnisse anlegen
if not os.path.exists(os.path.join(basedir, "pdf")):
    os.mkdir(os.path.join(basedir, "pdf"), 0o777)
if not os.path.exists(os.path.join(basedir, "log")):
    os.mkdir(os.path.join(basedir, "log"), 0o777)
    logDateinummer = 0
else:
    logListe = os.listdir(os.path.join(basedir, "log"))
    logListe.sort()
    if len(logListe) > 5:
        os.remove(os.path.join(basedir, "log/" + logListe[0]))
datum = datetime.datetime.strftime(datetime.datetime.today(), "%Y%m%d")
# logHandler = logging.FileHandler(os.path.join(basedir, "log/" + datum + "_gerigdt.log"), mode="a", encoding="utf_8")

# logLevel = logging.WARNING
# logForm = logging.Formatter("{asctime} {levelname:8}: {message}", "%d.%m.%Y %H:%M:%S", "{")
# if len(sys.argv) == 2 and sys.argv[1].upper() == "DEBUG":
#     logLevel = logging.DEBUG
# logHandler.setFormatter(logForm)
# logger = logging.getLogger(__name__)
# logger.addHandler(logHandler)
# logger.setLevel(logLevel)

def versionVeraltet(versionAktuell:str, versionVergleich:str):
    """
    Vergleicht zwei Versionen im Format x.x.x
    Parameter:
        versionAktuell:str
        versionVergleich:str
    Rückgabe:
        True, wenn versionAktuell veraltet
    """
    versionVeraltet= False
    hunderterBase = int(versionVergleich.split(".")[0])
    zehnerBase = int(versionVergleich.split(".")[1])
    einserBase = int(versionVergleich.split(".")[2])
    hunderter = int(versionAktuell.split(".")[0])
    zehner = int(versionAktuell.split(".")[1])
    einser = int(versionAktuell.split(".")[2])
    if hunderterBase > hunderter:
        versionVeraltet = True
    elif hunderterBase == hunderter:
        if zehnerBase >zehner:
            versionVeraltet = True
        elif zehnerBase == zehner:
            if einserBase > einser:
                versionVeraltet = True
    return versionVeraltet

# Sicherstellen, dass Icon in Windows angezeigt wird
try:
    from ctypes import windll # type: ignore
    mayappid = "gdttools.gerigdt"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(mayappid)
except ImportError:
    pass

class MainWindow(QMainWindow):
    barthelTests = ["Essen", "Baden", "Körperpflege (Rasieren, Zähneputzen)", "An- und Auskleiden", "Stuhlkontrolle", "Urinkontrolle", "Toilettenbenutzung", "Bett-/ (Roll-) Stuhltransfer", "Mobilität", "Treppensteigen"]
    barthelMaxPunkte = [10, 5, 5, 10, 10, 10, 10, 15, 15, 10]
    barthelEssen = ["Unfähig, alleine zu essen (0)", "Braucht etwas Hilfe (5)", "Selbstständig, benötigt keine Hilfe (10)"]
    barthelBaden = ["Abhängig von fremder Hilfe (0)", "Selbstständig, benötigt keine Hilfe (5)"]
    barthelKoerperpflege = ["Abhängig von fremder Hilfe (0)", "Selbstständig, benötigt keine Hilfe (5)"]
    barthelAnAuskleiden = ["Unfähig, sich allein an- und Auszuziehen (0)", "Benötigt etwas Hilfe, kann aber ca. 50% allein durchführen (5)", "Selbstständig, benötigt keine Hilfe (10)"]
    barthelStuhlkontrolle = ["Inkontinent (0)", "Gelegentlich inkontinent (max. 1x pro Woche) (5)", "Ständig kontinent (10)"]
    barthelUrinkontrolle = ["Inkontinent (0)", "Gelegentlich inkontinent (max. 1x pro Tag) (5)", "Ständig kontinent (10)"]
    barthelToilettenbenutzung = ["Abhängig von fremder Hilfe (0)", "Benötigt Hilfe wegen fehlenden Gleichgewichts oder beim Ausziehen (5)", "Selbstständig, benötigt keine Hilfe (10)"]
    barthelBettRollstuhltransfer = ["Abhängig von fremder Hilfe, fehlende Sitzbalance (0)", "Erhebliche physische Hilfe beim Transfer erforderlich, Sitzen selbstständig (5)", "Geringe physische bzw. verbale Hilfe oder Beaufsichtigung erforderlich (10)", "Selbstständig, benötigt keine Hilfe (15)"]
    barthelMobilitaet = ["Immobil bzw. Strecke < 50 m (0)", "Unabhängig mit Rollstuhl inklusive Ecken, Strecke > 50 m (5)", "Unterstütztes Gehen möglich, Strecke > 50 m (10)", "Selbstständiges Gehen möglich (Hilfsmittel erlaubt), Strecke > 50 m (15)"]
    barthelTreppensteigen = ["Unfähig, allein Treppe zu steigen (0)", "Benötigt Hilfe oder Überwachung beim Treppensteigen (5)", "Selbstständiges Treppensteigen möglich (10)"]
    timedUpGo = ["< 10 Sekunden - keine Mobilitätseinschränkung", "11-19 Sekunden - leichte, i. d. R. irrelevante Mobilitätseinschränkung", "20-29 Sekunden - abklärungsbedürftige, relevante Mobilitätseinschränkung", "> 30 Sekunden - starke Mobilitätseinschränkung"]
    kognitiveFunktion = ["Keine oder leichte Einschränkung", "Mittlere Einschränkung", "Schwere Einschränkung"]
    pflegegrad = ["1", "2", "3", "4", "5", "Nicht vorhanden/unbekannt", "Beantragt"]
    verfuegungen = ["Patientenverfügung", "Vorsorgevollmacht", "Betreuungsverfügung"]

    # Mainwindow zentrieren
    def resizeEvent(self, e):
        mainwindowBreite = e.size().width()
        mainwindowHoehe = e.size().height()
        ag = self.screen().availableGeometry()
        screenBreite = ag.size().width()
        screenHoehe = ag.size().height()
        left = screenBreite / 2 - mainwindowBreite / 2
        top = screenHoehe / 2 - mainwindowHoehe / 2
        self.setGeometry(left, top, mainwindowBreite, mainwindowHoehe)

    # Statusmeldungen ändern
    def changeStatus(self, statusnummer:int, statustext:str, rot = False, gruen = False):
        """
            Ändert eine Statusmeldung
            Parameter:
                statusnummer:int
                statustext:str
                rot:boolean (optional)
        """
        self.statusanzeigeLabel[statusnummer].setText(self.statusanzeigeLabelTexte[statusnummer] + ": " + statustext)
        if rot:
            self.statusanzeigeLabel[statusnummer].setStyleSheet("font-weight:normal; color:rgb(200,0,0)")
        elif gruen:
            self.statusanzeigeLabel[statusnummer].setStyleSheet("font-weight:normal; color:rgb(0,150,0)")

    def __init__(self):
        super().__init__()

        # config.ini lesen
        ersterStart = False
        updateSafePath = ""
        if sys.platform == "win32":
            logger.logger.info("Plattform: win32")
            updateSafePath = os.path.expanduser("~\\appdata\\local\\gerigdt")
        else:
            logger.logger.info("Plattform: nicht win32")
            updateSafePath = os.path.expanduser("~/.config/gerigdt")
        self.configPath = updateSafePath
        self.configIni = configparser.ConfigParser()
        if os.path.exists(os.path.join(updateSafePath, "config.ini")):
            logger.logger.info("config.ini in " + updateSafePath + " exisitert")
            self.configPath = updateSafePath
        elif os.path.exists(os.path.join(basedir, "config.ini")):
            logger.logger.info("config.ini in " + updateSafePath + " exisitert nicht")
            try:
                if (not os.path.exists(updateSafePath)):
                    logger.logger.info(updateSafePath + " exisitert nicht")
                    os.makedirs(updateSafePath, 0o777)
                    logger.logger.info(updateSafePath + "erzeugt")
                shutil.copy(os.path.join(basedir, "config.ini"), updateSafePath)
                logger.logger.info("config.ini von " + basedir + " nach " + updateSafePath + " kopiert")
                self.configPath = updateSafePath
                ersterStart = True
            except:
                logger.logger.error("Problem beim Kopieren der config.ini von " + basedir + " nach " + updateSafePath)
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Problem beim Kopieren der Konfigurationsdatei. GeriGDT wird mit Standardeinstellungen gestartet.", QMessageBox.StandardButton.Ok)
                mb.exec()
                self.configPath = basedir
        else:
            logger.logger.critical("config.ini fehlt")
            mb = QMessageBox(QMessageBox.Icon.Critical, "Hinweis von GeriGDT", "Die Konfigurationsdatei config.ini fehlt. GeriGDT kann nicht gestartet werden.", QMessageBox.StandardButton.Ok)
            mb.exec()
            sys.exit()
        self.configIni.read(os.path.join(self.configPath, "config.ini"))
        self.gdtImportVerzeichnis = self.configIni["GDT"]["gdtimportverzeichnis"]
        self.gdtExportVerzeichnis = self.configIni["GDT"]["gdtexportverzeichnis"]
        self.kuerzelgerigdt = self.configIni["GDT"]["kuerzelgerigdt"]
        self.kuerzelpraxisedv = self.configIni["GDT"]["kuerzelpraxisedv"]
        self.benutzernamen = self.configIni["Benutzer"]["namen"].split("::")
        self.benutzerkuerzel = self.configIni["Benutzer"]["kuerzel"].split("::")
        self.aktuelleBenuztzernummer = 0
        self.version = self.configIni["Allgemein"]["version"]
        self.dokuVerzeichnis = self.configIni["Allgemein"]["dokuverzeichnis"]
        self.vorherigeDokuLaden = (self.configIni["Allgemein"]["vorherigedokuladen"] == "1")

        # Nachträglich hinzufefügte Options
        # 3.10.2
        self.eulagelesen = False
        if self.configIni.has_option("Allgemein", "eulagelesen"):
            self.eulagelesen = self.configIni["Allgemein"]["eulagelesen"] == "True"
        # 3.10.0
        self.benutzeruebernehmen = False
        if self.configIni.has_option("Allgemein", "benutzeruebernehmen"):
            self.benutzeruebernehmen = (self.configIni["Allgemein"]["benutzeruebernehmen"] == "1")
        self.einrichtunguebernehmen = False
        if self.configIni.has_option("Allgemein", "einrichtunguebernehmen"):
            self.einrichtunguebernehmen = (self.configIni["Allgemein"]["einrichtunguebernehmen"] == "1")
        self.einrichtung = ""
        if self.configIni.has_option("Benutzer", "einrichtung"):
            self.einrichtung = self.configIni["Benutzer"]["einrichtung"]
        # 3.9.0
        self.pdfbezeichnung = "Geriatrisches Basisassessment"
        if self.configIni.has_option("Allgemein", "pdfbezeichnung"):
            self.pdfbezeichnung = self.configIni["Allgemein"]["pdfbezeichnung"]
        # 3.2.2
        self.pdferstellen = False
        if self.configIni.has_option("Allgemein", "pdferstellen"):
            self.pdferstellen = (self.configIni["Allgemein"]["pdferstellen"] == "1")
        self.bmiuebernehmen = False
        if self.configIni.has_option("Allgemein", "bmiuebernehmen"):
            self.bmiuebernehmen = (self.configIni["Allgemein"]["bmiuebernehmen"] == "1")
        # /Nachträglich hinzufefügte Options

        z = self.configIni["GDT"]["zeichensatz"]
        self.zeichensatz = gdt.GdtZeichensatz.IBM_CP437
        if z == "1":
            self.zeichensatz = gdt.GdtZeichensatz.BIT_7
        elif z == "3":
            self.zeichensatz = gdt.GdtZeichensatz.ANSI_CP1252
        self.lanr = self.configIni["Erweiterungen"]["lanr"]
        self.lizenzschluessel = self.configIni["Erweiterungen"]["lizenzschluessel"]

        # Prüfen, ob Lizenzschlüssel unverschlüsselt
        if len(self.lizenzschluessel) == 29:
            logger.logger.info("Lizenzschlüssel unverschlüsselt")
            self.configIni["Erweiterungen"]["lizenzschluessel"] = gdttoolsL.GdtToolsLizenzschluessel.krypt(self.lizenzschluessel)
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                    self.configIni.write(configfile)
        else:
            self.lizenzschluessel = gdttoolsL.GdtToolsLizenzschluessel.dekrypt(self.lizenzschluessel)

        # Prüfen, ob EULA gelesen
        if not self.eulagelesen:
            de = dialogEula.Eula()
            de.exec()
            if de.checkBoxZustimmung.isChecked():
                self.eulagelesen = True
                self.configIni["Allgemein"]["eulagelesen"] = "True"
                with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                    self.configIni.write(configfile)
                logger.logger.info("EULA zugestimmt")
            else:
                mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Ohne Zustimmung der Lizenzvereinbarung kann GeriGDT nicht gestartet werden.", QMessageBox.StandardButton.Ok)
                mb.exec()
                sys.exit()

        # Grundeinstellungen bei erstem Start
        if ersterStart:
            logger.logger.info("Erster Start")
            mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von GeriGDT", "Vermutlich starten Sie GeriGDT das erste Mal auf diesem PC.\nMöchten Sie jetzt die Grundeinstellungen vornehmen?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.setDefaultButton(QMessageBox.StandardButton.Yes)
            if mb.exec() == QMessageBox.StandardButton.Yes:
                self.einstellungenLanrLizenzschluessel()
                self.einstellungenGdt()
                self.einstellungenAllgemein()
                self.einstellungenBenutzer(True)

        # Version vergleichen und gegebenenfalls aktualisieren
        configIniBase = configparser.ConfigParser()
        try:
            configIniBase.read(os.path.join(basedir, "config.ini"))
            if versionVeraltet(self.version, configIniBase["Allgemein"]["version"]):
                # Version aktualisieren
                self.configIni["Allgemein"]["version"] = configIniBase["Allgemein"]["version"]
                self.configIni["Allgemein"]["releasedatum"] = configIniBase["Allgemein"]["releasedatum"] 
                # config.ini aktualisieren
                # 3.9.0 -> 3.10.0: ["Allgemein"]["benutzeruebernehmen"], ["Allgemein"]["einrichtunguebernehmen"] und ["Benutzer"]["einrichtung"] hinzufügen
                if not self.configIni.has_option("Allgemein", "benutzeruebernehmen"):
                    self.configIni["Allgemein"]["benutzeruebernehmen"] = "0"
                if not self.configIni.has_option("Allgemein", "einrichtunguebernehmen"):
                    self.configIni["Allgemein"]["einrichtunguebernehmen"] = "0"
                if not self.configIni.has_option("Benutzer", "einrichtung"):
                    self.configIni["Benutzer"]["einrichtung"] = ""
                # 3.8.0 -> 3.9.0: ["Allgemein"]["pdfbezeichnung"] hinzufügen
                if not self.configIni.has_option("Allgemein", "pdfbezeichnung"):
                    self.configIni["Allgemein"]["pdfbezeichnung"] = "Geriatrisches Basisassessment"
                # 3.2.1 -> 3.2.2: ["Allgemein"]["pdferstellen"], ["Allgemein"]["bmiuebernehmen"] und pdf-Ordner hinzufügen
                if not self.configIni.has_option("Allgemein", "pdferstellen"):
                    self.configIni["Allgemein"]["pdferstellen"] = "0"
                if not self.configIni.has_option("Allgemein", "bmiuebernehmen"):
                    self.configIni["Allgemein"]["bmiuebernehmen"] = "0"
                # /config.ini aktualisieren

                with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                    self.configIni.write(configfile)
                self.version = self.configIni["Allgemein"]["version"]
                logger.logger.info("Version auf " + self.version + " aktualisiert")
                # Prüfen, ob EULA gelesen
                de = dialogEula.Eula(self.version)
                de.exec()
                self.eulagelesen = de.checkBoxZustimmung.isChecked()
                self.configIni["Allgemein"]["eulagelesen"] = str(self.eulagelesen)
                with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                    self.configIni.write(configfile)
                if self.eulagelesen:
                    logger.logger.info("EULA zugestimmt")
                else:
                    logger.logger.info("EULA nicht zugestimmt")
                    mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Ohne  Zustimmung zur Lizenzvereinbarung kann GeriGDT nicht gestartet werden.", QMessageBox.StandardButton.Ok)
                    mb.exec()
                    sys.exit()
        except SystemExit:
            sys.exit()
        except:
            logger.logger.error("Problem beim Aktualisieren auf Version " + configIniBase["Allgemein"]["version"])
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Problem beim Aktualisieren auf Version " + configIniBase["Allgemein"]["version"], QMessageBox.StandardButton.Ok)
            mb.exec()

        # Add-Ons freigeschaltet?
        self.addOnsFreigeschaltet = gdttoolsL.GdtToolsLizenzschluessel.lizenzErteilt(self.lizenzschluessel, self.lanr, gdttoolsL.SoftwareId.GERIGDT)
        
        jahr = datetime.datetime.now().year
        copyrightJahre = "2023"
        if jahr > 2023:
            copyrightJahre = "2023-" + str(jahr)
        self.setWindowTitle("GeriGDT V" + self.version + " (\u00a9 Fabian Treusch - GDT-Tools " + copyrightJahre + ")")
        font = QFont()
        font.setBold(False)
        fontBold = QFont()
        fontBold.setBold(True)
        fontBoldGross = QFont()
        fontBoldGross.setBold(True)
        fontBoldGross.setPixelSize(16)
        # GDT-Datei laden
        gd = gdt.GdtDatei()
        self.patId = "-"
        self.name = "-"
        self.geburtsdatum = "-"
        self.groesse = "-"
        self.gewicht = "-"
        mbErg = QMessageBox.StandardButton.Yes
        try:
            # Prüfen, ob PVS-GDT-ID eingetragen
            senderId = self.configIni["GDT"]["idpraxisedv"]
            if senderId == "":
                senderId = None
            gd.laden(self.gdtImportVerzeichnis + "/" + self.kuerzelgerigdt + self.kuerzelpraxisedv + ".gdt", self.zeichensatz, senderId)
            self.patId = str(gd.getInhalt("3000"))
            self.name = str(gd.getInhalt("3102")) + " " + str(gd.getInhalt("3101"))
            logger.logger.info("PatientIn " + self.name + " (ID: " + self.patId + ") geladen")
            self.geburtsdatum = str(gd.getInhalt("3103"))[0:2] + "." + str(gd.getInhalt("3103"))[2:4] + "." + str(gd.getInhalt("3103"))[4:8]
            if gd.getInhalt("3622") and gd.getInhalt("3623"):
                self.groesse = str(gd.getInhalt("3622"))
                self.gewicht = str(gd.getInhalt("3623"))
            elif self.pdferstellen and self.bmiuebernehmen:
                mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Körpergröße und -gewicht wurden nicht vom Praxisverwaltungssystem übermittelt. Der BMI kann daher für die PDF-Dateierstellung nicht berechnent werden.", QMessageBox.StandardButton.Ok)
                mb.exec()
        except (IOError, gdtzeile.GdtFehlerException) as e:
            logger.logger.warning("Fehler beim Laden der GDT-Datei: " + str(e))
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Fehler beim Laden der GDT-Datei:\n" + str(e) + "\n\nSoll GeriGDT dennoch geöffnet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
            mb.button(QMessageBox.StandardButton.No).setText("Nein")
            mb.setDefaultButton(QMessageBox.StandardButton.No)
            mbErg = mb.exec()
        if mbErg == QMessageBox.StandardButton.Yes:
            self.widget = QWidget()
            self.widget.installEventFilter(self)
            mainLayout = QVBoxLayout()
            kopfLayout = QHBoxLayout()
            kopfLayout.setAlignment(Qt.AlignmentFlag.AlignRight)
            titelLabel = QLabel("Geriatrisches Basisassessment")
            titelLabel.setStyleSheet("font-weight:bold;font-size:26px")
            kopfLayout.addWidget(titelLabel)
            # Statusanzeige aufbauen
            self.statusanzeigeLabelTexte = ["Von PVS erzeugte GDT-Datei", "Vorherige Dokumentation geladen vom"]
            self.statusanzeigeStatustext = []
            for statustext in range(len(self.statusanzeigeLabelTexte)):
                self.statusanzeigeStatustext.append("")
            self.statusanzeigeLabel = []
            groupboxStatusanzeigeLayout = QGridLayout()
            groupboxStatusanzeige = QGroupBox(title="Statusanzeige")
            groupboxStatusanzeige.setStyleSheet("font-weight:bold")
            i = 0
            for text in self.statusanzeigeLabelTexte:
                if i == 1:
                    self.buttonAlteUntersuchung = QPushButton()
                    reloadIcon = QIcon(os.path.join(basedir, "icons/reload.png"))
                    self.buttonAlteUntersuchung.setIcon(reloadIcon)
                    self.buttonAlteUntersuchung.setEnabled(False)
                    self.buttonAlteUntersuchung.setToolTip("Funktion nicht verfügbar")
                    self.buttonAlteUntersuchung.clicked.connect(self.vorherigeUntersuchungWiederherstellen) # type: ignore
                    groupboxStatusanzeigeLayout.addWidget(self.buttonAlteUntersuchung, i, 0)
                self.statusanzeigeLabel.append(QLabel(text + ": -"))
                self.statusanzeigeLabel[i].setStyleSheet("font-weight:normal")
                groupboxStatusanzeigeLayout.addWidget(self.statusanzeigeLabel[i], i, 1)
                i += 1
            groupboxStatusanzeige.setLayout(groupboxStatusanzeigeLayout)
            kopfLayout.addStretch()
            kopfLayout.addWidget(groupboxStatusanzeige)
            if self.patId !="-":
                self.changeStatus(0, "geladen")
            else:
                self.changeStatus(0, "nicht geladen", True)
            testLayout = QGridLayout()
            barthelLabel = QLabel(text="Barthel-Index")
            barthelLabel.setFont(fontBoldGross)
            self.labelBarthelGesamt = QLabel("Gesamt: 100 Punkte")
            self.labelBarthelGesamt.setFont(fontBoldGross)
            self.labelBarthelGesamt.setStyleSheet("color:rgb(100,100,100)")
            groupboxLayout = QVBoxLayout()
            groupboxBarthelEssen = QGroupBox(title="Essen")
            self.radiobuttonBarhelEssen = []
            for radio in self.barthelEssen:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelEssen.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelEssen[len(self.barthelEssen) - 1].setChecked(True)
            groupboxBarthelEssen.setLayout(groupboxLayout)
            groupboxBarthelEssen.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelBaden = QGroupBox(title="Baden")
            self.radiobuttonBarhelBaden = []
            for radio in self.barthelBaden:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelBaden.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelBaden[len(self.barthelBaden) - 1].setChecked(True)
            groupboxBarthelBaden.setLayout(groupboxLayout)
            groupboxBarthelBaden.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelKoerperpflege = QGroupBox(title="Körperpflege (Rasieren, Zähneputzen)")
            self.radiobuttonBarhelKoerperpflege = []
            for radio in self.barthelKoerperpflege:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelKoerperpflege.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelKoerperpflege[len(self.barthelKoerperpflege) - 1].setChecked(True)
            groupboxBarthelKoerperpflege.setLayout(groupboxLayout)
            groupboxBarthelKoerperpflege.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelAnAuskleiden = QGroupBox(title="An- und Auskleiden")
            self.radiobuttonBarhelAnAuskleiden = []
            for radio in self.barthelAnAuskleiden:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelAnAuskleiden.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelAnAuskleiden[len(self.barthelAnAuskleiden) - 1].setChecked(True)
            groupboxBarthelAnAuskleiden.setLayout(groupboxLayout)
            groupboxBarthelAnAuskleiden.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelStuhlkontrolle = QGroupBox(title="Stuhlkontrolle")
            self.radiobuttonBarhelStuhlkontrolle = []
            for radio in self.barthelStuhlkontrolle:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelStuhlkontrolle.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelStuhlkontrolle[len(self.barthelStuhlkontrolle) - 1].setChecked(True)
            groupboxBarthelStuhlkontrolle.setLayout(groupboxLayout)
            groupboxBarthelStuhlkontrolle.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelUrinkontrolle = QGroupBox(title="Urinkontrolle")
            self.radiobuttonBarhelUrinkontrolle = []
            for radio in self.barthelUrinkontrolle:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelUrinkontrolle.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelUrinkontrolle[len(self.barthelUrinkontrolle) - 1].setChecked(True)
            groupboxBarthelUrinkontrolle.setLayout(groupboxLayout)
            groupboxBarthelUrinkontrolle.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelToilettenbenutzung = QGroupBox(title="Toilettenbenutzung")
            self.radiobuttonBarhelToilettenbenutzung = []
            for radio in self.barthelToilettenbenutzung:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelToilettenbenutzung.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelToilettenbenutzung[len(self.barthelToilettenbenutzung) - 1].setChecked(True)
            groupboxBarthelToilettenbenutzung.setLayout(groupboxLayout)
            groupboxBarthelToilettenbenutzung.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxBarthelBettRollstuhltransfer = QGroupBox(title="Bett-/ (Roll-)-Stuhltransfer")
            self.radiobuttonBarhelBettRollstuhltransfer = []
            for radio in self.barthelBettRollstuhltransfer:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelBettRollstuhltransfer.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelBettRollstuhltransfer[len(self.barthelBettRollstuhltransfer) - 1].setChecked(True)
            groupboxBarthelBettRollstuhltransfer.setLayout(groupboxLayout)
            groupboxBarthelBettRollstuhltransfer.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelMobilitaet = QGroupBox(title="Mobilität")
            self.radiobuttonBarhelMobilitaet = []
            for radio in self.barthelMobilitaet:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelMobilitaet.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelMobilitaet[len(self.barthelMobilitaet) - 1].setChecked(True)
            groupboxBarthelMobilitaet.setLayout(groupboxLayout)
            groupboxBarthelMobilitaet.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxBarthelTreppensteigen = QGroupBox(title="Treppensteigen")
            self.radiobuttonBarhelTreppensteigen = []
            for radio in self.barthelTreppensteigen:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonBarhelTreppensteigen.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonBarhelTreppensteigen[len(self.barthelTreppensteigen) - 1].setChecked(True)
            groupboxBarthelTreppensteigen.setLayout(groupboxLayout)
            groupboxBarthelTreppensteigen.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxTimedUpGo = QGroupBox(title="Timed \"Up and Go\"")
            self.radiobuttonTimedUpGo = []
            for radio in self.timedUpGo:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonTimedUpGo.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonTimedUpGo[0].setChecked(True)
            groupboxTimedUpGo.setLayout(groupboxLayout)
            groupboxTimedUpGo.setFont(fontBold)
            
            groupboxLayout = QVBoxLayout()
            groupboxKognitiveFunktion = QGroupBox("Kognitive Funktion")
            self.radiobuttonKognitiveFunktion = []
            for radio in self.kognitiveFunktion:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonKognitiveFunktion.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonKognitiveFunktion[0].setChecked(True)
            groupboxKognitiveFunktion.setLayout(groupboxLayout)
            groupboxKognitiveFunktion.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxPflegegrad = QGroupBox("Pflegegrad")
            self.radiobuttonPflegegrad = []
            for radio in self.pflegegrad:
                rb = QRadioButton(text=radio)
                rb.setFont(font)
                rb.clicked.connect(self.barthelGeklickt) # type: ignore
                self.radiobuttonPflegegrad.append(rb)
                groupboxLayout.addWidget(rb)
            self.radiobuttonPflegegrad[len(self.pflegegrad) - 2].setChecked(True)
            groupboxPflegegrad.setLayout(groupboxLayout)
            groupboxPflegegrad.setFont(fontBold)

            groupboxLayout = QVBoxLayout()
            groupboxVerfuegungen = QGroupBox("Verfügungen/Vollmachten")
            self.checkboxVerfuegungen = []
            for checkbox in self.verfuegungen:
                cb = QCheckBox(text=checkbox)
                cb.setFont(font)
                cb.stateChanged.connect(self.verfuegungGeklickt) # type: ignore
                self.checkboxVerfuegungen.append(cb)
                groupboxLayout.addWidget(cb)
            groupboxVerfuegungen.setLayout(groupboxLayout)
            groupboxVerfuegungen.setFont(fontBold)

            testLayout.addWidget(barthelLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            testLayout.addWidget(self.labelBarthelGesamt, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            testLayout.addWidget(groupboxBarthelEssen, 1, 0)
            testLayout.addWidget(groupboxBarthelBaden, 2, 0)
            testLayout.addWidget(groupboxBarthelKoerperpflege, 3, 0)
            testLayout.addWidget(groupboxBarthelAnAuskleiden, 4, 0)
            testLayout.addWidget(groupboxBarthelStuhlkontrolle, 5, 0)
            testLayout.addWidget(groupboxBarthelUrinkontrolle, 1, 1)
            testLayout.addWidget(groupboxBarthelToilettenbenutzung, 2, 1)
            testLayout.addWidget(groupboxBarthelBettRollstuhltransfer, 3, 1)
            testLayout.addWidget(groupboxBarthelMobilitaet, 4, 1)
            testLayout.addWidget(groupboxBarthelTreppensteigen, 5, 1)
            testLayout.addWidget(groupboxTimedUpGo, 1, 2)
            testLayout.addWidget(groupboxKognitiveFunktion, 2, 2)
            testLayout.addWidget(groupboxPflegegrad, 3, 2)
            testLayout.addWidget(groupboxVerfuegungen, 4, 2)
            datenLayoutH = QHBoxLayout()
            datenLayoutG = QGridLayout()
            labelName = QLabel("Name:")
            labelPatId = QLabel("Pat.-ID:")
            labelUntDat = QLabel("Untersuchungsdatum:")
            labelDokuVon = QLabel("Dokumentiert von:")
            labelNameGdt = QLabel()
            labelPatIdGdt = QLabel()
            labelNameGdt.setText(self.name)
            labelPatIdGdt.setText(self.patId)
            untdat = QDate()
            self.untdatEdit = QDateEdit()
            self.untdatEdit.setDate(untdat.currentDate())
            self.untdatEdit.setDisplayFormat("dd.MM.yyyy")
            self.untdatEdit.setCalendarPopup(True)
            self.untdatEdit.userDateChanged.connect(self.datumGeaendert) # type: ignore
            self.dokuvonComboBox = QComboBox()
            self.dokuvonComboBox.currentIndexChanged.connect(self.benutzerGewechselt)# type: ignore
            benutzernamen = self.configIni["Benutzer"]["namen"].split("::")
            benutzerkuerzel = self.configIni["Benutzer"]["kuerzel"].split("::")
            for i in range(len(benutzernamen)):
                self.dokuvonComboBox.addItem(benutzernamen[i] + " (" + benutzerkuerzel[i] + ")")
            datenLayoutG.addWidget(labelName, 0, 0)
            datenLayoutG.addWidget(labelNameGdt, 0, 1)
            datenLayoutG.addWidget(labelPatId, 1, 0)
            datenLayoutG.addWidget(labelPatIdGdt, 1, 1)
            datenLayoutG.addWidget(labelUntDat, 2, 0)
            datenLayoutG.addWidget(self.untdatEdit, 2, 1)
            datenLayoutG.addWidget(labelDokuVon, 3, 0)
            datenLayoutG.addWidget(self.dokuvonComboBox, 3, 1)
            self.pushbuttonDatenSenden = QPushButton("Daten senden")
            self.pushbuttonDatenSenden.setFixedSize(QSize(160, 80))
            if self.patId == "-":
                self.pushbuttonDatenSenden.setEnabled(False)
                self.pushbuttonDatenSenden.setToolTip("Senden nicht möglich, da keine GDT-Datei vom PVS geladen")
            self.pushbuttonDatenSenden.clicked.connect(self.datenSendenClicked) # type: ignore
            datenLayoutH.addLayout(datenLayoutG)
            datenLayoutH.addSpacing(20)
            datenLayoutH.addWidget(self.pushbuttonDatenSenden)
            testLayout.addLayout(datenLayoutH, 5, 2)
            mainLayout.addLayout(kopfLayout)
            mainLayout.addLayout(testLayout)
            self.widget.setLayout(mainLayout)

            self.setCentralWidget(self.widget)

            # Menü
            menubar = self.menuBar()
            anwendungMenu = menubar.addMenu("")
            aboutAction = QAction(self)
            aboutAction.setMenuRole(QAction.MenuRole.AboutRole)
            aboutAction.triggered.connect(self.ueberGeriGdt) # type: ignore
            aboutAction.setShortcut(QKeySequence("Ctrl+Ü"))
            updateAction = QAction("Auf Update prüfen", self)
            updateAction.setMenuRole(QAction.MenuRole.ApplicationSpecificRole)
            updateAction.triggered.connect(self.updatePruefung) # type: ignore
            updateAction.setShortcut(QKeySequence("Ctrl+U"))
            einstellungenMenu = menubar.addMenu("Einstellungen")
            einstellungenAllgemeinAction = QAction("Allgemeine Einstellungen", self)
            einstellungenAllgemeinAction.triggered.connect(lambda neustartfrage: self.einstellungenAllgemein(True)) # type: ignore
            einstellungenAllgemeinAction.setShortcut(QKeySequence("Ctrl+E"))
            einstellungenGdtAction = QAction("GDT-Einstellungen", self)
            einstellungenGdtAction.triggered.connect(lambda neustartfrage: self.einstellungenGdt(True)) # type: ignore
            einstellungenGdtAction.setShortcut(QKeySequence("Ctrl+G"))
            einstellungenBenutzerAction = QAction("BenutzerInnen verwalten", self)
            einstellungenBenutzerAction.triggered.connect(lambda neustartfrage: self.einstellungenBenutzer(True)) # type: ignore
            einstellungenBenutzerAction.setShortcut(QKeySequence("Ctrl+B"))
            einstellungenErweiterungenAction = QAction("LANR/Lizenzschlüssel", self)
            einstellungenErweiterungenAction.triggered.connect(lambda neustartfrage: self.einstellungenLanrLizenzschluessel(True)) # type: ignore
            einstellungenErweiterungenAction.setShortcut(QKeySequence("Ctrl+L"))
            einstellungenImportExportAction = QAction("Im- /Exportieren", self)
            einstellungenImportExportAction.triggered.connect(self.einstellungenImportExport) # type: ignore
            einstellungenImportExportAction.setShortcut(QKeySequence("Ctrl+I"))
            einstellungenImportExportAction.setMenuRole(QAction.MenuRole.NoRole)
            hilfeMenu = menubar.addMenu("Hilfe")
            hilfeWikiAction = QAction("GeriGDT Wiki", self)
            hilfeWikiAction.triggered.connect(self.gerigdtWiki) # type: ignore
            hilfeWikiAction.setShortcut(QKeySequence("Ctrl+W"))
            hilfeUpdateAction = QAction("Auf Update prüfen", self)
            hilfeUpdateAction.triggered.connect(self.updatePruefung) # type: ignore
            hilfeUpdateAction.setShortcut(QKeySequence("Ctrl+U"))
            hilfeUeberAction = QAction("Über GeriGDT", self)
            hilfeUeberAction.setMenuRole(QAction.MenuRole.NoRole)
            hilfeUeberAction.triggered.connect(self.ueberGeriGdt) # type: ignore
            hilfeUeberAction.setShortcut(QKeySequence("Ctrl+Ü"))
            hilfeLogExportieren = QAction("Log-Verzeichnis exportieren", self)
            hilfeLogExportieren.triggered.connect(self.logExportieren) # type: ignore
            hilfeLogExportieren.setShortcut(QKeySequence("Ctrl+D"))
            
            anwendungMenu.addAction(aboutAction)
            anwendungMenu.addAction(updateAction)
            einstellungenMenu.addAction(einstellungenAllgemeinAction)
            einstellungenMenu.addAction(einstellungenGdtAction)
            einstellungenMenu.addAction(einstellungenBenutzerAction)
            einstellungenMenu.addAction(einstellungenErweiterungenAction)
            einstellungenMenu.addAction(einstellungenImportExportAction)
            hilfeMenu.addAction(hilfeWikiAction)
            hilfeMenu.addSeparator()
            hilfeMenu.addAction(hilfeUpdateAction)
            hilfeMenu.addSeparator()
            hilfeMenu.addAction(hilfeUeberAction)
            hilfeMenu.addSeparator()
            hilfeMenu.addAction(hilfeLogExportieren)
            
            # Updateprüfung auf Github
            try:
                self.updatePruefung(meldungNurWennUpdateVerfuegbar=True)
            except Exception as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Updateprüfung nicht möglich.\nBitte überprüfen Sie Ihre Internetverbindung.", QMessageBox.StandardButton.Ok)
                mb.exec()
                logger.logger.warning("Updateprüfung nicht möglich: " + str(e))
            
            # Gegebenenfalls vorheriges Untersuchungsergebnis verwenden
            if self.vorherigeDokuLaden:
                self.mitVorherigerUntersuchungAusfuellen()
                
        else:
            sys.exit()

    def eventFilter(self, object, event:QEvent):
        if object == self.widget and event.type() == QEvent.Type.KeyPress and (event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter): # type:ignore
            self.pushbuttonDatenSenden.click()
            return True
        return False

    def mitVorherigerUntersuchungAusfuellen(self):
        pfad = self.dokuVerzeichnis + "/" + self.patId
        doku = ""
        if os.path.exists(self.dokuVerzeichnis):
            if os.path.exists(pfad) and len(os.listdir(pfad)) > 0:
                dokus = [d for d in os.listdir(pfad) if os.path.isfile(pfad + "/" + d)]
                dokus.sort()
                try:
                    with open(pfad + "/" + dokus[len(dokus) - 1], "r") as d:
                        doku = d.read().strip()
                except IOError as e:
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Fehler beim Lesen der vorherigen Dokumentation.\nSoll GeriGDT neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                    mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                    mb.button(QMessageBox.StandardButton.No).setText("Nein")
                    if mb.exec() == QMessageBox.StandardButton.Yes:
                        os.execl(sys.executable, __file__, *sys.argv)
        else:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Das Archivierungsverzeichnis " + self.dokuVerzeichnis + "  ist nicht erreichbar. Vorherige Assessments können daher nicht geladen werden.\nFalls es sich um eine Netzwerkfreigabe handeln sollte, stellen Sie die entsprechende Verbindung sicher und starten GeriGDT neu.\nSoll GeriGDT neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mb.setDefaultButton(QMessageBox.StandardButton.Yes)
            mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
            mb.button(QMessageBox.StandardButton.No).setText("Nein")
            if mb.exec() == QMessageBox.StandardButton.Yes:
                os.execl(sys.executable, __file__, *sys.argv)  
                
        if doku != "" and len(doku) != 21 and len(doku) != 22: # 22 für Verfügungen (seit Version 3.8.0)
            mb = QMessageBox(QMessageBox.Icon.Information, "Hinweis von GeriGDT", "Die vorherige Dokumentation von " + self.name + " ist nicht lesbar.", QMessageBox.StandardButton.Ok)
            mb.exec()
            doku = ""
        if doku != "" and self.addOnsFreigeschaltet:
            # Untersuchungsdatum
            untdat = self.dokuZusammenfassungLesen(doku)[0]
            self.changeStatus(1, untdat.toString("dd.MM.yyyy"), gruen=True)
            self.buttonAlteUntersuchung.setEnabled(True)
            self.buttonAlteUntersuchung.setToolTip("Vorheriges Untersuchungsergebnis wiederherstellen")
            # Barthel ausfüllen
            barthelGesamt = self.dokuZusammenfassungLesen(doku)[1]
            self.radiobuttonBarhelEssen[int(barthelGesamt[0] / 5)].setChecked(True)
            self.radiobuttonBarhelBaden[int(barthelGesamt[1] / 5)].setChecked(True)
            self.radiobuttonBarhelKoerperpflege[int(barthelGesamt[2] / 5)].setChecked(True)
            self.radiobuttonBarhelAnAuskleiden[int(barthelGesamt[3] / 5)].setChecked(True)
            self.radiobuttonBarhelStuhlkontrolle[int(barthelGesamt[4] / 5)].setChecked(True)
            self.radiobuttonBarhelUrinkontrolle[int(barthelGesamt[5] / 5)].setChecked(True)
            self.radiobuttonBarhelToilettenbenutzung[int(barthelGesamt[6] / 5)].setChecked(True)
            self.radiobuttonBarhelBettRollstuhltransfer[int(barthelGesamt[7] / 5)].setChecked(True)
            self.radiobuttonBarhelMobilitaet[int(barthelGesamt[8] / 5)].setChecked(True)
            self.radiobuttonBarhelTreppensteigen[int(barthelGesamt[9] / 5)].setChecked(True)
            self.barthelGeklickt()
            # Rest ausfüllen
            tug = int(self.dokuZusammenfassungLesen(doku)[2])
            pg = int(self.dokuZusammenfassungLesen(doku)[3])
            kf = int(self.dokuZusammenfassungLesen(doku)[4])
            vf = int(self.dokuZusammenfassungLesen(doku)[5])
            if pg == 0:
                pg = 5
            elif pg == 5:
                pg = 6
            else:
                pg -= 1
            self.radiobuttonTimedUpGo[tug].setChecked(True)
            self.radiobuttonPflegegrad[pg].setChecked(True)
            self.radiobuttonKognitiveFunktion[kf].setChecked(True)
            self.checkboxVerfuegungen[0].setChecked(vf & 0b001 == 0b001)
            self.checkboxVerfuegungen[1].setChecked(vf & 0b010 == 0b010)
            self.checkboxVerfuegungen[2].setChecked(vf & 0b100 == 0b100)
        else:
            self.changeStatus(1, "-")
            self.buttonAlteUntersuchung.setEnabled(False)
            self.buttonAlteUntersuchung.setToolTip("Funktion nicht verfügbar")

    def barthelGeklickt(self):
        barthelGesamt = self.barthelBerechnen()[1]
        self.labelBarthelGesamt.setText("Gesamt: " + str(barthelGesamt) + " Punkte")

    def verfuegungGeklickt(self):
        pass

    def vorherigeUntersuchungWiederherstellen(self):
        if self.vorherigeDokuLaden:
            self.mitVorherigerUntersuchungAusfuellen()

    def datumGeaendert(self, datum):
        gewaehltesDatum = QDate(datum)
        if gewaehltesDatum.daysTo(QDate().currentDate()) < 0:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Das Untersuchungsdatum darf nicht in der Zukunft liegen.", QMessageBox.StandardButton.Ok)
            mb.exec()

    def benutzerGewechselt(self):
        self.aktuelleBenuztzernummer = self.dokuvonComboBox.currentIndex()

    def updatePruefung(self, meldungNurWennUpdateVerfuegbar = False):
        response = requests.get("https://api.github.com/repos/retconx/gerigdt/releases/latest")
        githubRelaseTag = response.json()["tag_name"]
        latestVersion = githubRelaseTag[1:] # ohne v
        if versionVeraltet(self.version, latestVersion):
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Die aktuellere GeriGDT-Version " + latestVersion + " ist auf <a href='https://www.github.com/retconx/gerigdt/releases'>Github</a> verfügbar.", QMessageBox.StandardButton.Ok)
            mb.setTextFormat(Qt.TextFormat.RichText)
            mb.exec()
        elif not meldungNurWennUpdateVerfuegbar:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Sie nutzen die aktuelle GeriGDT-Version.", QMessageBox.StandardButton.Ok)
            mb.exec()

    def ueberGeriGdt(self):
        de = dialogUeberGeriGdt.UeberGeriGdt()
        de.exec()

    def logExportieren(self):
        if (os.path.exists(os.path.join(basedir, "log"))):
            downloadPath = ""
            if sys.platform == "win32":
                downloadPath = os.path.expanduser("~\\Downloads")
            else:
                downloadPath = os.path.expanduser("~/Downloads")
            try:
                if shutil.copytree(os.path.join(basedir, "log"), os.path.join(downloadPath, "Log_GeriGDT"), dirs_exist_ok=True):
                    shutil.make_archive(os.path.join(downloadPath, "Log_GeriGDT"), "zip", root_dir=os.path.join(downloadPath, "Log_GeriGDT"))
                    shutil.rmtree(os.path.join(downloadPath, "Log_GeriGDT"))
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Das Log-Verzeichnis wurde in den Ordner " + downloadPath + " kopiert.", QMessageBox.StandardButton.Ok)
                    mb.exec()
            except Exception as e:
                mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Problem beim Download des Log-Verzeichnisses: " + str(e), QMessageBox.StandardButton.Ok)
                mb.exec()
        else:
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Das Log-Verzeichnis wurde nicht gefunden.", QMessageBox.StandardButton.Ok)
            mb.exec() 

    def einstellungenAllgemein(self, neustartfrage = False):
        de = dialogEinstellungenAllgemein.EinstellungenAllgemein(self.configPath)
        if de.exec() == 1:
            self.configIni["Allgemein"]["dokuverzeichnis"] = de.lineEditArchivierungsverzeichnis.text()
            self.configIni["Allgemein"]["vorherigedokuladen"] = "0"
            if de.checkboxVorherigeDokuLaden.isChecked():
                self.configIni["Allgemein"]["vorherigedokuladen"] = "1"
            self.configIni["Allgemein"]["pdferstellen"] = "0"
            if de.checkboxPdfErstellen.isChecked():
                self.configIni["Allgemein"]["pdferstellen"] = "1"  
            self.configIni["Allgemein"]["bmiuebernehmen"] = "0"
            if de.checkboxBmiUebernehmen.isChecked():
                self.configIni["Allgemein"]["bmiuebernehmen"] = "1"  
            self.configIni["Allgemein"]["pdfbezeichnung"] = de.lineEditPdfBezeichnung.text()
            self.configIni["Allgemein"]["benutzeruebernehmen"] = "0"
            if de.checkboxBenutzerUebernehmen.isChecked():
                self.configIni["Allgemein"]["benutzeruebernehmen"] = "1"
            self.configIni["Allgemein"]["einrichtunguebernehmen"] = "0"
            if de.checkboxEinrichtungUebernehmen.isChecked():
                self.configIni["Allgemein"]["einrichtunguebernehmen"] = "1"
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von GeriGDT", "Damit die Einstellungsänderungen wirksam werden, sollte GeriGDT neu gestartet werden.\nSoll GeriGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    os.execl(sys.executable, __file__, *sys.argv)

    def einstellungenGdt(self, neustartfrage = False):
        de = dialogEinstellungenGdt.EinstellungenGdt(self.configPath)
        if de.exec() == 1:
            self.configIni["GDT"]["idgerigdt"] = de.lineEditGeriGdtId.text()
            self.configIni["GDT"]["idpraxisedv"] = de.lineEditPraxisEdvId.text()
            self.configIni["GDT"]["gdtimportverzeichnis"] = de.lineEditImport.text()
            self.configIni["GDT"]["gdtexportverzeichnis"] = de.lineEditExport.text()
            self.configIni["GDT"]["kuerzelgerigdt"] = de.lineEditGeriGdtKuerzel.text()
            self.configIni["GDT"]["kuerzelpraxisedv"] = de.lineEditPraxisEdvKuerzel.text()
            self.configIni["GDT"]["zeichensatz"] = str(de.aktuelleZeichensatznummer + 1)
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von GeriGDT", "Damit die Einstellungsänderungen wirksam werden, sollte GeriGDT neu gestartet werden.\nSoll GeriGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    os.execl(sys.executable, __file__, *sys.argv)

    def einstellungenBenutzer(self, neustartfrage = False):
        de = dialogEinstellungenBenutzer.EinstellungenBenutzer(self.configPath)
        if de.exec() == 1:
            self.configIni["Benutzer"]["einrichtung"] = de.lineEditEinrichtungsname.text()
            namen = []
            kuerzel = []
            for i in range(5):
                if de.lineEditNamen[i].text() != "":
                    namen.append(de.lineEditNamen[i].text())
                    kuerzel.append(de.lineEditKuerzel[i].text())
            self.configIni["Benutzer"]["namen"] = "::".join(namen)
            self.configIni["Benutzer"]["kuerzel"] = "::".join(kuerzel)
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von GeriGDT", "Damit die Einstellungsänderungen wirksam werden, sollte GeriGDT neu gestartet werden.\nSoll GeriGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    os.execl(sys.executable, __file__, *sys.argv)

    def einstellungenLanrLizenzschluessel(self, neustartfrage = False):
        de = dialogEinstellungenLanrLizenzschluessel.EinstellungenProgrammerweiterungen(self.configPath)
        if de.exec() == 1:
            self.configIni["Erweiterungen"]["lanr"] = de.lineEditLanr.text()
            self.configIni["Erweiterungen"]["lizenzschluessel"] = gdttoolsL.GdtToolsLizenzschluessel.krypt(de.lineEditLizenzschluessel.text())
            with open(os.path.join(self.configPath, "config.ini"), "w") as configfile:
                self.configIni.write(configfile)
            if neustartfrage:
                mb = QMessageBox(QMessageBox.Icon.Question, "Hinweis von GeriGDT", "Damit die Einstellungsänderungen wirksam werden, sollte GeriGDT neu gestartet werden.\nSoll GeriGDT jetzt neu gestartet werden?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                mb.setDefaultButton(QMessageBox.StandardButton.Yes)
                mb.button(QMessageBox.StandardButton.Yes).setText("Ja")
                mb.button(QMessageBox.StandardButton.No).setText("Nein")
                if mb.exec() == QMessageBox.StandardButton.Yes:
                    os.execl(sys.executable, __file__, *sys.argv)

    def einstellungenImportExport(self):
        de = dialogEinstellungenImportExport.EinstellungenImportExport(self.configPath)
        if de.exec() == 1:
            pass
    
    def gerigdtWiki(self, link):
        QDesktopServices.openUrl("https://www.github.com/retconx/gerigdt/wiki")

    def barthelBerechnen(self):
        """
        Berechnet den aktuell gewählten Bathelindex
        Rückgabe:
            Tupel(barthelEinzel:list, barthelGesamt.int)
        """
        barthelTests = [self.radiobuttonBarhelEssen, self.radiobuttonBarhelBaden, self.radiobuttonBarhelKoerperpflege, self.radiobuttonBarhelAnAuskleiden, self.radiobuttonBarhelStuhlkontrolle, self.radiobuttonBarhelUrinkontrolle, self.radiobuttonBarhelToilettenbenutzung, self.radiobuttonBarhelBettRollstuhltransfer, self.radiobuttonBarhelMobilitaet, self.radiobuttonBarhelTreppensteigen]
        barthelEinzel = []
        barthelGesamt = 0
        for barthelTest in barthelTests:
            zaehler = 0
            for punkt in barthelTest:
                if punkt.isChecked():
                    barthelGesamt += zaehler * 5
                    barthelEinzel.append(zaehler * 5)
                zaehler += 1
        return (barthelEinzel, barthelGesamt)

    def datenSendenClicked(self):
        logger.logger.info("Daten senden geklickt")
        barthelEinzel, barthelGesamt = self.barthelBerechnen()

        # GDT-Datei erzeugen
        sh = gdt.SatzHeader(gdt.Satzart.DATEN_EINER_UNTERSUCHUNG_UEBERMITTELN_6310, self.configIni["GDT"]["idpraxisedv"], self.configIni["GDT"]["idgerigdt"], self.zeichensatz, "2.10", "Fabian Treusch - GDT-Tools", "GeriGDT", self.version, self.patId)
        gd = gdt.GdtDatei()
        logger.logger.info("GdtDatei-Instanz erzeugt")
        gd.erzeugeGdtDatei(sh.getSatzheader())
        logger.logger.info("Satzheader 6310 erzeugt")
        self.datum = "{:>02}".format(str(self.untdatEdit.date().day())) + "{:>02}".format(str(self.untdatEdit.date().month())) + str(self.untdatEdit.date().year())
        jetzt = QTime().currentTime()
        uhrzeit = "{:>02}".format(str(jetzt.hour())) + "{:>02}".format(str(jetzt.minute())) + str(jetzt.second())
        logger.logger.info("Untersuchungsdatum/ -uhrzeit festgelegt")
        gd.addZeile("6200", self.datum)
        gd.addZeile("6201", uhrzeit)
        gd.addZeile("8402", "ALLG00")
        # PDF hinzufügen
        if self.pdferstellen:
            gd.addZeile("6302", "geri_ass")
            gd.addZeile("6303", "pdf")
            gd.addZeile("6304", self.pdfbezeichnung)
            gd.addZeile("6305", os.path.join(basedir, "pdf/geriass_temp.pdf"))
        # Barthel
        testBarthelEssen = gdt.GdtTest("ESSEN", "Essen", str(barthelEinzel[0]), " von 10 Punkten")
        gd.addTest(testBarthelEssen)
        testBarthelBaden = gdt.GdtTest("BADEN", "Baden", str(barthelEinzel[1]), " von 5 Punkten")
        gd.addTest(testBarthelBaden)
        testBarthelKoerperpflege = gdt.GdtTest("KOERPERPFLEGE", "Körperpflege (Rasieren, Zähneputzen)", str(barthelEinzel[2]), " von 5 Punkten")
        gd.addTest(testBarthelKoerperpflege)
        testBarthelAnAuskleiden = gdt.GdtTest("ANAUSKLEIDEN", "An- und Auskleiden", str(barthelEinzel[3]), " von 10 Punkten")
        gd.addTest(testBarthelAnAuskleiden)
        testBarthelStuhlkontrolle = gdt.GdtTest("STUHLKONTROLLE", "Stuhlkontrolle", str(barthelEinzel[4]), " von 10 Punkten")
        gd.addTest(testBarthelStuhlkontrolle)
        testBarthelUrinkontrolle = gdt.GdtTest("URINKONTROLLE", "Urinkontrolle", str(barthelEinzel[5]), " von 10 Punkten")
        gd.addTest(testBarthelUrinkontrolle)
        testBarthelToilettenbenutzung = gdt.GdtTest("TOILETTENBENUTZUNG", "Toilettenbenutzung", str(barthelEinzel[6]), " von 10 Punkten")
        gd.addTest(testBarthelToilettenbenutzung)
        testBarthelBettRolstuhlTransfer = gdt.GdtTest("BETTROLLSTUHLTRANSFER", "Bett-/ (Roll)-Stuhltransfer", str(barthelEinzel[7]), " von 15 Punkten")
        gd.addTest(testBarthelBettRolstuhlTransfer)
        testBarthelMobilitaet = gdt.GdtTest("MOBILITAET", "Mobilität", str(barthelEinzel[8]), " von 15 Punkten")
        gd.addTest(testBarthelMobilitaet)
        testBarthelTreppensteigen = gdt.GdtTest("TREPPENSTEIGEN", "Treppensteigen", str(barthelEinzel[9]), " von 10 Punkten")
        gd.addTest(testBarthelTreppensteigen)
        logger.logger.info("Barthel-Tests erzeugt")
        # Timed Up and Go
        tugErgebnis = ""
        tugErgebnisInt = 0
        for rb in self.radiobuttonTimedUpGo:
            if rb.isChecked():
                tugErgebnis = rb.text()
                break
            else:
                tugErgebnisInt += 1
        testTimedUpGo = gdt.GdtTest("TIMEDUPGO", "Timed \"Up and Go\"", tugErgebnis, "")
        gd.addTest(testTimedUpGo)
        logger.logger.info("TuG-Test erzeugt")
        # Kognitive Funktion
        kfErgebnis = ""
        kfErgebnisInt = 0
        for rb in self.radiobuttonKognitiveFunktion:
            if rb.isChecked():
                kfErgebnis = rb.text()
                break
            else:
                kfErgebnisInt += 1
        testKognitiveFunktion = gdt.GdtTest("KOGNITIVEFUNKTION", "Kognitive Funktion", kfErgebnis, "")
        gd.addTest(testKognitiveFunktion)
        logger.logger.info("KF-Test erzeugt")
        # Pflegegrad
        pgErgebnis = ""
        pgErgebnisInt = 0
        for rb in self.radiobuttonPflegegrad:
            if rb.isChecked():
                pgErgebnis = rb.text()
                break
            else:
                pgErgebnisInt += 1
        testPflegegrad = gdt.GdtTest("PFLEGEGRAD", "Pflegegrad", pgErgebnis, "")
        gd.addTest(testPflegegrad)
        logger.logger.info("PG-Test erzeugt")
        # Verfügungen
        vfErgebis = 0b000
        if self.checkboxVerfuegungen[0].isChecked(): # Patientenverfügung
            vfErgebis += 0b001
        if self.checkboxVerfuegungen[1].isChecked(): # Vorsorgevollmacht
            vfErgebis += 0b010
        if self.checkboxVerfuegungen[2].isChecked(): # Betreuungsverfügung
            vfErgebis += 0b100
        vfTextListe = []
        for i in range(3):
            if self.checkboxVerfuegungen[i].isChecked():
                vfTextListe.append(self.verfuegungen[i])
        vfErgebnistext = "Keine Angabe"
        if len(vfTextListe) > 0:
            vfErgebnistext = ", ".join(vfTextListe)
        testVerfuegungen = gdt.GdtTest("VERFUEGUNGEN", "Verfügungen/Vollmachten", vfErgebnistext, "")
        gd.addTest(testVerfuegungen)
        logger.logger.info("Verfügungen-Test erzeugt")
        # Benutzer
        ak = self.aktuelleBenuztzernummer
        gd.addZeile("6227", "Dokumentiert von " + self.benutzerkuerzel[int(self.aktuelleBenuztzernummer)])
        # Befund
        gd.addZeile("6220", "Barthel-Index: " + str(barthelGesamt) + " Punkte")
        gd.addZeile("6221", "Timed \"Up and Go\": " + str(tugErgebnis))
        gd.addZeile("6221", "Kognitive Funktion: " + str(kfErgebnis))
        gd.addZeile("6221", "Pflegegrad: " + str(pgErgebnis))
        gd.addZeile("6221", "Verfügungen/Vollmachten: " + vfErgebnistext)
        logger.logger.info("Befund/Fremdbefunde erzeugt")

        # PDF erzeugen
        if self.pdferstellen:
            logger.logger.info("PDF-Erstellung aktiviert")
            # BMI berechnen
            bmi = 0
            if self.pdferstellen and self.bmiuebernehmen and self.groesse != "-" and self.gewicht != "-":
                logger.logger.info("BMI-Berechung aktiviert")
                # Prüfen, ob Grüße in cm oder m
                groesse = float(self.groesse.replace(",", "."))
                if groesse > 3:
                    groesse /= 100
                bmi = "{:.1f}".format(float(self.gewicht.replace(",", ".")) / groesse / groesse)

            pdf = geriasspdf.geriasspdf ("P", "mm", "A4")
            logger.logger.info("FPDF-Instanz erzeugt")
            pdf.add_page()
            bmiText = ""
            if bmi != 0:
                bmiText = ", BMI: " + bmi + " kg/m\u00b2"
            pdf.set_font("helvetica", "", 14)
            pdf.cell(0, 10, "von " + self.name + " (* " + self.geburtsdatum + bmiText + ")", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
            untdat = "{:>02}".format(str(self.untdatEdit.date().day())) + "." + "{:>02}".format(str(self.untdatEdit.date().month())) + "." + str(self.untdatEdit.date().year())
            beurteiltVon = ""
            if self.benutzeruebernehmen:
                beurteiltVon = " von " + self.benutzernamen[int(self.aktuelleBenuztzernummer)]
            if self.einrichtunguebernehmen:
                beurteiltVon += " (" + self.einrichtung + ")"
            pdf.cell(0, 6, "Beurteilt am " + untdat + beurteiltVon, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 14)
            pdf.set_font(style="B")
            pdf.cell(0, 8, "Barthel-Index", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="")
            # Barthel
            pdf.set_fill_color(240,240,240)
            i = 0
            for test in self.barthelTests:
                pdf.cell(90, 10, test + ":", fill=(i % 2 == 0))
                if barthelEinzel[i] != self.barthelMaxPunkte[i]:
                    pdf.set_font(style="B")
                pdf.cell(0, 10, str(barthelEinzel[i]) +  " von " + str(self.barthelMaxPunkte[i]) + " Punkten", align="R", new_x="LMARGIN", new_y="NEXT", fill=(i % 2 == 0))
                pdf.set_font(style="")
                i += 1
            pdf.set_font(style="B")
            pdf.cell(90, 10, "Gesamt:", border="T")
            pdf.cell(0, 10, str(barthelGesamt) + " Punkte", border="T", align="R", new_x="LMARGIN", new_y="NEXT")
            # Timed "Up and Go"
            pdf.cell(0, 4, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="B")
            pdf.cell(0, 8, "Timed \u0022Up and Go\u0022-Test", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="")
            pdf.cell(30, 10, "Ergebnis:")
            pdf.cell(0, 10, tugErgebnis, align="R", new_x="LMARGIN", new_y="NEXT")
            # Kognitive Funktion
            pdf.cell(0, 4, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="B")
            pdf.cell(0, 8, "Kognitive Funktion", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="")
            pdf.cell(30, 10, "Ergebnis:")
            pdf.cell(0, 10, kfErgebnis, align="R", new_x="LMARGIN", new_y="NEXT")
            # Pflegegrad
            pdf.cell(0, 4, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="B")
            pdf.cell(0, 8, "Pflegegrad", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="")
            pdf.cell(30, 10, "Ergebnis:")
            pdf.cell(0, 10, pgErgebnis, align="R", new_x="LMARGIN", new_y="NEXT")
            # Verfügungen
            pdf.cell(0, 4, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="B")
            pdf.cell(0, 8, "Erstellte Verfügungen/Vollmachten", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(style="")
            pdf.cell(0, 10, vfErgebnistext)

            pdf.set_y(-30)
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, "Generiert von GeriGDT V" + self.version + " (\u00a9 GDT-Tools " + str(datetime.date.today().year) + ")", align="R")
            logger.logger.info("PDF-Seite aufgebaut")
            try:
                pdf.output(os.path.join(basedir, "pdf/geriass_temp.pdf"))
                logger.logger.info("PDF-Output nach " + os.path.join(basedir, "pdf/geriass_temp.pdf") + " erfolgreich")
            except:
                logger.logger.error("Fehler bei PDF-Output nach " + os.path.join(basedir, "pdf/geriass_temp.pdf"))
            
        # GDT-Datei exportieren
        if not gd.speichern(self.gdtExportVerzeichnis + "/" + self.kuerzelpraxisedv + self.kuerzelgerigdt + ".gdt", self.zeichensatz):
            logger.logger.error("Fehler bei GDT-Dateiexport nach " + self.gdtExportVerzeichnis + "/" + self.kuerzelpraxisedv + self.kuerzelgerigdt + ".gdt")
            mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "GDT-Export nicht möglich.\nBitte überprüfen Sie die Angabe des Exportverzeichnisses.", QMessageBox.StandardButton.Ok)
            mb.exec()
        else:
            dokuZusammenfassung = self.dokuZusammenfassen(barthelEinzel, tugErgebnisInt, kfErgebnisInt, pgErgebnisInt, vfErgebis)
            if self.dokuVerzeichnis != "":
                if os.path.exists(self.dokuVerzeichnis):
                    speicherdatum = str(self.untdatEdit.date().year()) + "{:>02}".format(str(self.untdatEdit.date().month())) + "{:>02}".format(str(self.untdatEdit.date().day()))
                    try:
                        if not os.path.exists(self.dokuVerzeichnis + "/" + self.patId):
                            os.mkdir(self.dokuVerzeichnis + "/" + self.patId, 0o777)
                            logger.logger.info("Dokuverzeichnis für PatId " + self.patId + " erstellt")
                        with open(self.dokuVerzeichnis + "/" + self.patId + "/" + speicherdatum + "_" + self.patId + ".gba", "w") as zf:
                            zf.write(dokuZusammenfassung)
                            logger.logger.info("Doku für PatId " + self.patId + " archiviert")
                    except IOError as e:
                        logger.logger.error("IO-Fehler beim Speichern der Doku von PatId " + self.patId)
                        mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Fehler beim Speichern der Dokumentation\n" + str(e), QMessageBox.StandardButton.Ok)
                        mb.exec()
                    except:
                        logger.logger.error("Nicht-IO-Fehler beim Speichern der Doku von PatId " + self.patId)
                        raise
                else:
                    logger.logger.warning("Dokuverzeichnis existiert nicht")
                    mb = QMessageBox(QMessageBox.Icon.Warning, "Hinweis von GeriGDT", "Speichern der Dokumentation nicht möglich\nBitte überprüfen Sie die Angabe des Dokumentations-Speicherverzeichnisses.", QMessageBox.StandardButton.Ok)
                    mb.exec()
        sys.exit()

    def dokuZusammenfassen(self, barthel:list, timedUpGo:int, kognitiveFunktion:int, pflegegrad:int, verfuegungen:int):
        # Untersuchungsdatum TTMMJJJJ + 10x Barthel hexadezimal + TUG 0-3 + PG 0-6 (unbekannt = 0) + KF 0-2
        zusammenfassung = self.datum
        for b in barthel:
            punkte = int(b)
            punkteHex = hex(punkte).upper()
            zusammenfassung += punkteHex[2]
        pflegegrad += 1
        if pflegegrad == 6:
            pflegegrad = 0
        elif pflegegrad == 7:
            pflegegrad = 6
        zusammenfassung += str(timedUpGo) + str(pflegegrad) + str(kognitiveFunktion) + str(verfuegungen)
        return zusammenfassung
    
    def dokuZusammenfassungLesen(self, zusammenfassung:str):
        jahr = int(zusammenfassung[4:8])
        monat = int(zusammenfassung[2:4])
        tag = int(zusammenfassung[0:2])
        datum = QDate(jahr, monat, tag)
        barthelGesamt = []
        for bt in zusammenfassung[8:18]:
            barthelGesamt.append(int(bt, 16))
        tug = zusammenfassung[18]
        pg = zusammenfassung[19]
        kf = zusammenfassung[20]
        # Gegebenenfalls Verfügungen (ab Version 3.8.0)
        vf = 0
        if len(zusammenfassung) == 22:
            vf = zusammenfassung[21]
        return (datum, barthelGesamt, tug, pg, kf, vf)
    
    def gdtToolsLinkGeklickt(self, link):
        QDesktopServices.openUrl(link)
    
app = QApplication(sys.argv)
qt = QTranslator()
filename = "qtbase_de"
directory = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
qt.load(filename, directory)
app.installTranslator(qt)
app.setWindowIcon(QIcon(os.path.join(basedir, "icons/program.png")))
window = MainWindow()
window.show()

app.exec()