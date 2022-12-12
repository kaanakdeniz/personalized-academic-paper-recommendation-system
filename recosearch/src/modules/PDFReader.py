from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os
from urllib.request import urlretrieve as get


class PDFReader:

    def __init__(self):

        self.codec = 'utf-8'
        self.laparams = LAParams()

    def read_text(self, path):

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        device = TextConverter(
            rsrcmgr, retstr, codec=self.codec, laparams=self.laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        with open(path, 'rb') as file:
            for page in PDFPage.get_pages(file):
                interpreter.process_page(page)

        text = retstr.getvalue()

        device.close()
        retstr.close()

        return text

    def download_and_read(self, title, url):

        filepath = "dataset/"+title+".pdf"
        get(url, filepath)
        text = self.read_text(filepath)
        return text

