import random, datetime
from enum import Enum

class Gueltigkeit(Enum):
    DREISSIGTAGE = "D"
    SECHSMONATE = "H"
    EINJAHR = "J"
    UNBEFRISTET = "U"

class SoftwareId(Enum):
    GERIGDT = "A"
    OPTIGDT = "B"

datumstellen = [2, 3, 13, 17, 19, 21, 23]
reststellen = [0, 1, 5, 7, 8, 12, 14, 16, 18, 22, 24]
checksummestellen = [9, 10, 11]

class GdtToolsLizenzschluessel:
    @staticmethod
    def lanrGueltig(lanr:str, lizenzschluessel:str):
        """Prüft eine LANR/Lizenzschlüsselkombination auf Gültigkeit
        Parameter:
            lanr:str
            Lizenzschlüssel:str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            True oder False
        """
        lizenzschluesselOhneBindestrich = lizenzschluessel.replace("-", "")
        quersummeLanr = 0
        for stelle in lanr:
            quersummeLanr += int(stelle)
        quersummeLanrAusLizenzschluessel = lizenzschluesselOhneBindestrich[4] + lizenzschluesselOhneBindestrich[15]
        return "{:02X}".format(quersummeLanr) == quersummeLanrAusLizenzschluessel
    
    @staticmethod
    def getErstellungsdatum(lizenzschluessel:str):
        """
        Gibt das Erstellungsdatum eines Lizenzschlüssels zurück
        Parameter:
            Lizenzschlüssel:str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            Erstellungsdatum im Format TTMMJJJJ
        """
        lizenzschluesselOhneBindestrich = lizenzschluessel.replace("-", "")
        datumHex = ""
        for stelle in datumstellen:
            datumHex += lizenzschluesselOhneBindestrich[stelle]
        return "{:08}".format(int(datumHex, 16))
    
    @staticmethod
    def checksummeKorrekt(lizenzschluessel:str):
        """
        Prüft die Checksumme eines Lizenzschluessels
        Parameter:
            Lizenzschlüssel: str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            True oder False
        """
        lizenzschluesselOhneBindestrich = lizenzschluessel.replace("-", "")
        checksummeHexGelesen = ""
        for stelle in checksummestellen:
            checksummeHexGelesen += lizenzschluesselOhneBindestrich[stelle]
        # Checksumme berechnen
        checksummeBerechnet = 0
        i = 0
        for stelle in lizenzschluesselOhneBindestrich:
            if i < 9 or i > 11:
                checksummeBerechnet += ord(stelle)
            i += 1
        checksummeBerechnetHex = "{:02X}".format(checksummeBerechnet)
        return checksummeBerechnetHex == checksummeHexGelesen
    
    @staticmethod
    def getGueltigkeitsdauer(lizenzschluessel:str):
        """Gibt die Gültigkeitsdauer eines Lizenzschlüssels zurück
        Parameter: 
            Lizenzschlüssel: str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            Gültigkeitsdauer:Gültigkeit
        """
        lizenzschluesselOhneBindestrich = lizenzschluessel.replace("-", "")
        gueltigkeitsdauer = lizenzschluesselOhneBindestrich[6]
        return Gueltigkeit(gueltigkeitsdauer)
    
    @staticmethod
    def getSoftwareId(lizenzschluessel:str):
        """Gibt die Software-ID eines Lizenzschlüssels zurück
        Parameter: 
            Lizenzschlüssel: str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            Software-ID:SoftwareId
        """
        lizenzschluesselOhneBindestrich = lizenzschluessel.replace("-", "")
        softwareId = lizenzschluesselOhneBindestrich[20]
        return SoftwareId(softwareId)
    
    @staticmethod
    def gueltigBis(lizenzschluessel:str):
        """
        Gibt das maximale Gültigkeitsdatum eines Lizenzschlüssels zurück
        Parameter: 
            Lizenzschlüssel: str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            Gültigkeitsdatum:datetime.date (01.01.1900, wenn unbefristet)
        """
        erstellungsdatumTTMMJJJJ = str(GdtToolsLizenzschluessel.getErstellungsdatum(lizenzschluessel))
        erstellungstag = int(erstellungsdatumTTMMJJJJ[0:2])
        erstellungsmonat = int(erstellungsdatumTTMMJJJJ[2:4])
        erstellungsjahr = int(erstellungsdatumTTMMJJJJ[4:])
        erstellungsdatum = datetime.date(erstellungsjahr, erstellungsmonat, erstellungstag)
        gueltigkeit = GdtToolsLizenzschluessel.getGueltigkeitsdauer(lizenzschluessel)
        gueltigBis = datetime.date(1900, 1, 1)
        if gueltigkeit == Gueltigkeit.DREISSIGTAGE:
            gueltigBis = erstellungsdatum + datetime.timedelta(days=30)
        elif gueltigkeit == Gueltigkeit.SECHSMONATE:
            gueltigBis = erstellungsdatum + datetime.timedelta(days=190)
        elif gueltigkeit == Gueltigkeit.EINJAHR:
            gueltigBis = erstellungsdatum + datetime.timedelta(days=366)
        return gueltigBis
    
    @staticmethod
    def heuteGueltig(lizenzschluessel:str):
        """
        Prüft, ob ein Lizenzschlüssel heute gültig ist
        Parameter: 
            Lizenzschlüssel: str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
        Rückgabe:
            True oder False
        """
        heute = datetime.date.today()
        if GdtToolsLizenzschluessel.gueltigBis(lizenzschluessel) == datetime.date(1900,1 ,1):
            return True
        return GdtToolsLizenzschluessel.gueltigBis(lizenzschluessel) >= heute
    
    @staticmethod
    def lizenzErteilt(lizenzschluessel:str, lanr:str, softwareId:SoftwareId):
        """
        Prüft ob: Checksumme eines Lizenzschlüssels korrekt, LANR zum Lizenzschlüssel passt, der Lizenzschlüssel heute gültig ist, die Software-ID korrekt ist
        Parameter: 
            Lizenzschlüssel: str (XXXXX-XXXXX-XXXXX-XXXXX-XXXXX)
            LANR:str
            softwareId:SoftwareId
        """
        return lizenzschluessel != "" and lanr != "" and GdtToolsLizenzschluessel.checksummeKorrekt(lizenzschluessel) and GdtToolsLizenzschluessel.lanrGueltig(lanr, lizenzschluessel) and GdtToolsLizenzschluessel.heuteGueltig(lizenzschluessel) and GdtToolsLizenzschluessel.getSoftwareId(lizenzschluessel) == softwareId
    
    @staticmethod
    def checksummeLanrKorrekt(lanr:str):
        """
        Prüft, die Checksume einer LANR
        Parameter:
            LANR:str
        Rückgabe
            True oder False
        """
        summe = 0
        faktor = 4
        for i in range(6):
            summe += int(lanr[i]) * faktor
            if faktor == 4:
                faktor = 9
            else:
                faktor = 4
        checksumme = 10 - (summe % 10)
        if checksumme == 10:
            checksumme = 0
        return int(lanr[6]) == checksumme

