import os
from fpdf import FPDF

basedir = os.path.dirname(__file__)

class geriasspdf(FPDF):

    def header(self):
        #self.image(os.path.join(basedir, "icons/praxislogo.gif"), 10, 10, 25)
        self.set_font("helvetica", "B", 20)
        self.cell(0, 10, "Geriatrisches Basisassessment", align="C", new_x="LMARGIN", new_y="NEXT")
        #self.cell(0,10, new_x="LMARGIN", new_y="NEXT")
