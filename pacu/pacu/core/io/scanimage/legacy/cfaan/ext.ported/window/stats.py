from base64 import b64encode

from scipy import stats
from PyQt4.QtGui import QApplication, QMessageBox
from PyQt4.QtCore import Qt
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QRect, QUrl
from PyQt4.QtWebKit import QWebView
from pyqtgraph import GraphicsWindow, LabelItem

from ext.console import debug

def_css = '''
* {
    font-size: 0.95em;
}
ul {
    list-style-type: none;
    margin: 1px;
    padding: 1px;
}
html, body {
    width: 100%;
    height: 100%;
}
body {
    margin: 0;
    padding: 0;
    font-family: sans-serif;
}
'''
class TableRow(object):
    key = ''
    val = ''
    def __init__(self, key, val=''):
        self.key = key
        self.val = val
    def __str__(self):
        return '<tr><td>{}</td><td>{}</td></tr>'.format(self.key, self.val)

html_template = """
<table border="1" cellpadding="2">
    <tr>
        <td>Analysis</td>
        <td>Result</td>
    </tr>
    %s
</table>
<button id="btn1" name="export_variables">export variables</button>
<button id="btn2" name="export_response_values">export response values</button>
<button id="btn3" name="export_response_matrix">export response matrix</button>
<button id="btn4" name="perform_bootstrap">perform bootstrap</button>
"""
css_template = """
body {
}
button {
width: 100%;
}
table {
  width: 100%;
}
div.float {
    float: left;
}
"""
def toclipboard(values):
    clip = '\t'.join(values)
    cboard = QApplication.clipboard()
    cboard.clear(mode=cboard.Clipboard)
    cboard.setText(clip, mode=cboard.Clipboard)
class StatsWindow(QWebView):
    keys = 'osi cv dsi sigma opref tau rmax resi anova_f anova_p npix bv_per_pix bmean bstd'.split()
    osi        = TableRow('OSI')
    cv         = TableRow('CV')
    dsi        = TableRow('DSI')
    sigma      = TableRow('Sigma')
    opref      = TableRow('Opref')
    tau        = TableRow('tau')
    rmax       = TableRow('Rmax')
    resi       = TableRow('Residual')
    anova_f    = TableRow('ANOVA f')
    anova_p    = TableRow('ANOVA p')
    npix       = TableRow('Number of Pixels')
    bv_per_pix = TableRow('Blank Value per Pixel')
    bmean      = TableRow('Bootstrap mean')
    bstd       = TableRow('Bootstrap STD')
    @classmethod
    def from_geo(cls, main, *pos):
        self = cls()
        self.main = main
        self.setWindowTitle('Statistics')
        self.setGeometry(QRect(*pos))
        self.setContentsMargins(0,0,0,0)
        self.update_css(css_template)
        self.update_html()
        return self

    def bind_event(self):
        main_frame = self.page().mainFrame()
        main_frame.addToJavaScriptWindowObject('MainWindow', self)
        doc_element = main_frame.documentElement()
        doc_element.evaluateJavaScript("""
            var onclick = this.addEventListener("click", function(e) {
                MainWindow.handle_click(e.target.name);
            }, false);
        """)
    def unbind_event(self):
        main_frame = self.page().mainFrame()
        main_frame.addToJavaScriptWindowObject('MainWindow', self)
        doc_element = main_frame.documentElement()
        doc_element.evaluateJavaScript("""
            var onclick = this.removeEventListener(onclick);
        """)
    @QtCore.pyqtSlot(QtCore.QVariant)
    def handle_click(self, element_name):
        name = str(element_name.toString())
        try:
            getattr(self, 'do_%s' % name)()
        except Exception as e:
            print 'button handling error', type(e), e
    def do_(self): pass
    def do_export_variables(self):
        variables = [str(getattr(self, key).val) for key in self.keys]
        print 'TO CLIPBOARD', variables
        toclipboard(variables)
    def do_export_response_values(self):
        print 'export_response_values'
        self.main.export_menubar.copy_response_values_to_clipboard()
    def do_export_response_matrix(self):
        print 'export_response_matrix'
        self.main.export_menubar.copy_response_matrix_to_clipboard()
    def do_perform_bootstrap(self):
        print 'perform_bootstrap'
        if self.main.tiffFig.roi_current:
            QMessageBox.information(
                self, 'Bootstrap',
                'Performing 500 samples...It will take a few minutes.')
            response = self.main.tiffFig.roi_current.response
            rv, mean, std = response.bootstrap_stat()
            self.bmean.val = mean
            self.bstd.val = std
            self.update_html()
        else:
            QMessageBox.information(
                self, 'Bootstrap',
                'Please select a cell to perform bootstrap.')


    def update_css(self, css=''):
        qurl = QUrl("data:text/css;charset=utf-8;base64," + b64encode((def_css+css).encode('utf-8')))
        self.settings().setUserStyleSheetUrl(qurl)
    def update_html(self):
        self.unbind_event()
        rest = ''.join(str(getattr(self, key)) for key in self.keys)
        self.setHtml(html_template % rest)
        self.bind_event()
    def updateAnalysis(self, **kwargs):
        oris = kwargs['oris']
        blank = kwargs['blank']
        oris_stacked = [value for values in oris for value in values]

        self.osi.val = kwargs.get('osi')
        self.cv.val = kwargs.get('cv')
        self.dsi.val = kwargs.get('dsi')
        self.sigma.val = kwargs.get('sigma')
        self.opref.val = kwargs.get('opref')
        self.tau.val = kwargs.get('tau')
        self.rmax.val = kwargs.get('rmax')
        self.resi.val = kwargs.get('resi')

        self.npix.val = kwargs.get('npix')
        self.bv_per_pix.val = kwargs.get('mfs_npix')
        self.anova_f.val, self.anova_p.val = stats.f_oneway(blank, *oris)
        self.update_html()


# ttest_t_value, ttest_p_value = stats.ttest_ind(blank, oris_stacked, equal_var=False)
# krusk_h_value, krusk_p_value = stats.mstats.kruskalwallis(blank, *oris)
