from enum import Enum
from xml.etree import ElementTree
import os

import datetime

class TrendError(Exception):
    def __init__(self, message:str):
        self.message = message

    def __str__(self) -> str:
        return "TrendError: " + self.message
    
class XmlPfadExistiertNichtError(Exception):
    def __init__(self, pfad:str):
        self.pfad = pfad

    def __str__(self):
        return "XmlPfadExistiertNichtError: Der Pfad " + self.pfad + " existiert nicht."
    
class GdtTool(Enum):
    SCOREGDT = "scoregdt"
    GERIGDT = "gerigdt"

class Trend:
    def __init__(self, datum:datetime.datetime, ergebnis:str, interpretation:str):
        self.datum = datum
        self.ergebnis = ergebnis
        self.interpretation = interpretation

    def __str__(self):
        return self.datum.strftime("%d.%m.%Y") + ":\u0009" + self.ergebnis + "\u0009" + self.interpretation

    def getTrend(self) -> dict:
        """
        Gibt einen Trend als Tupel zurück (datum:datetime.datetime, ergebnis:str, interpretation:int)
        """
        return {"datum" : self.datum, "ergebnis" : self.ergebnis, "interpretation" : self.interpretation}
    
    def getXml(self) -> ElementTree.Element:
        """
        Gibt ein XML-Trend-Element zurück
        """
        trendElement = ElementTree.Element("trend")
        trendElement.set("datum", self.datum.strftime("%Y%m%d%H%M%S"))
        ergebnisElement = ElementTree.Element("ergebnis")
        ergebnisElement.text = self.ergebnis
        interpretationElement = ElementTree.Element("interpretation")
        interpretationElement.text = self.interpretation
        trendElement.append(ergebnisElement)
        trendElement.append(interpretationElement)
        return trendElement
    
class Test:
    MAXIMALE_TRENDANZAHL = 3
    def __init__(self, name:str, gruppe:str, tool:GdtTool):
        self.name = name
        self.gruppe = gruppe
        self.tool = tool
        self.anzahlTrends = 0
        self.datumListe = []
        self.ergebnisListe = []
        self.interpretationListe = []

    def __str__(self):
        return self.name + " (" + self.tool.value + ")"

    def getName(self):
        return self.name
    
    def getGruppe(self):
        return self.gruppe
    
    def getTool(self):
        return self.tool

    def addTrend(self, trend:Trend):
        """
        Fügt einen Trend hinzu. Falls die Trendanzahl die maximal zulässige überschreitet, wird der älteste Trend entfernt
        Parameter:
            trend:Trend
        """
        self.datumListe.append(trend.getTrend()["datum"])
        self.ergebnisListe.append(trend.getTrend()["ergebnis"])
        self.interpretationListe.append(trend.getTrend()["interpretation"])
        self.anzahlTrends += 1
        ### Ältesten Trend löschen, falls max. Trendanzahl erreicht
        if self.anzahlTrends > self.MAXIMALE_TRENDANZAHL:
            reihenfolge = sorted([i for i in range(self.anzahlTrends)], key=lambda x:self.datumListe[x], reverse=True)
            self.datumListe.pop(reihenfolge[len(reihenfolge) - 1])
            self.ergebnisListe.pop(reihenfolge[len(reihenfolge) - 1])
            self.interpretationListe.pop(reihenfolge[len(reihenfolge) - 1])
            self.anzahlTrends -= 1
    def getTest(self):
        return {"name" : self.name, "tool" :self.tool}
        
    def getLetzteTrends(self) -> list:
        """
        Gibt die aktuellsten Trends des Tests zurück
        Return:
            Liste von Tupels (Datum, Ergebnis, Interpretation)
        """
        trends = []
        reihenfolge = sorted([i for i in range(self.anzahlTrends)], key=lambda x:self.datumListe[x], reverse=True)
        for i in reihenfolge:
            trends.append(Trend(self.datumListe[i], self.ergebnisListe[i], self.interpretationListe[i]))
        # trends = [(self.datumListe[i], self.ergebnisListe[i], self.interpretationListe[i]) for i in reihenfolge]
        return trends
    
    def getXmlElement(self) -> ElementTree.Element:
        """
        Gibt ein XML-Test-Element zurück
        """
        testElement = ElementTree.Element("test")
        testElement.set("name", self.name)
        testElement.set("gruppe", self.gruppe)
        testElement.set("tool", self.tool.value)
        for trend in self.getLetzteTrends():
            trendElement = Trend(trend.getTrend()["datum"], trend.getTrend()["ergebnis"], trend.getTrend()["interpretation"]).getXml()
            testElement.append(trendElement)
        return testElement

    def speichereAlsNeueXmlDatei(self, pfad:str):
        """
        Speichert den Test als neue Xml-Datei
        Parameter:
            pfad:str
        """
        trendsElement = ElementTree.Element("trends")
        trendsElement.append(self.getXmlElement())
        tree = ElementTree.ElementTree(trendsElement)
        ElementTree.indent(tree)
        try:
            tree.write(pfad, "utf-8", True)
        except Exception as e:
            raise TrendError("Fehler beim Speichern der XML-Datei + " + pfad + ": " + str(e))
        
@staticmethod
def getTestAusXml(xmlTest:ElementTree.Element) -> Test:
    name = str(xmlTest.get("name"))
    gruppe = str(xmlTest.get("gruppe"))
    tool = GdtTool(str(xmlTest.get("tool")))
    test = Test(name, gruppe, tool)
    for trendElement in xmlTest.findall("trend"):
        jahr = int(str(trendElement.get("datum"))[:4])
        monat = int(str(trendElement.get("datum"))[4:6])
        tag = int(str(trendElement.get("datum"))[6:8])
        stunde = int(str(trendElement.get("datum"))[8:10])
        minute = int(str(trendElement.get("datum"))[10:12])
        sekunde = int(str(trendElement.get("datum"))[12:])
        datum = datetime.datetime(jahr, monat, tag, stunde, minute, sekunde)
        ergebnis = str(trendElement.findtext("ergebnis"))
        interpretation = str(trendElement.findtext("interpretation"))
        test.addTrend(Trend(datum, ergebnis, interpretation))
    return test

@staticmethod
def aktualisiereXmlDatei(test:Test, trend:Trend, pfad:str):
    """
    Fügt einer Trend-XML-Datei einen Test und einen Trend hinzu und speichert diese
    Parameter:
        test:Test
        trend:Trend
        pfad:str Pfad der Trend-XML-Datei
    Exception:
        TrendError bei Fehler beim Speichern
        XmlPfadExistiertNichtError, falls pfad nicht existiert
    """
    if os.path.exists(pfad):
        tree = ElementTree.parse(pfad)
        trendsElement = tree.getroot()
        tempTestElement = None
        for testElement in trendsElement.findall("test"):
            name = str(testElement.get("name"))
            gruppe = str(testElement.get("gruppe"))
            tool = str(testElement.get("tool"))
            if name == test.getName() and gruppe == test.getGruppe() and tool == test.getTool().value:
                tempTestElement = testElement
                break
        tempTest = test
        if tempTestElement != None:
            tempTest = getTestAusXml(tempTestElement)
            trendsElement.remove(tempTestElement)
        tempTest.addTrend(trend)
        trendsElement.append(tempTest.getXmlElement())
        try:
            ElementTree.indent(tree)
            tree.write(pfad, "utf-8", True)
        except Exception as e:
            raise TrendError("Fehler beim Speichern der XML-Datei + " + pfad + ": " + str(e))
    else:
        raise XmlPfadExistiertNichtError(pfad)
    
@staticmethod
def getTrends(trendPfad:str) -> ElementTree.Element:
    """
    Gibt den Inhalt einer Trend-XML-Datei zurück
    Parameter:
        trendPfad:str
    Return: 
        trends-Element
    Exception:
        XmlPfadExistiertNichtError, falls Pfad nicht existiert
    """
    pfad = os.path.join(trendPfad, "trends.xml")
    if os.path.exists(pfad):
        tree = ElementTree.parse(pfad)
        return tree.getroot()
    else:
        raise XmlPfadExistiertNichtError(pfad)