# Written by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014

from PyQt4.QtGui import QApplication, QMessageBox

from ext.console import debug
from parse_tuning import Response, Orientation

class DebugMenubar(object):
    def __init__(self, maingui):
        self.maingui = maingui
    def __call__(self, *args, **kwargs):
        main = self.maingui
        tiff = main.tiffFig
        st = main.stats
        trace = main.tiffFig.traceFig
        rf = tiff.responseFig
        meta = main.sfreq_meta
        cond = main.conditions
        rmax = main.rmax_by_sfreq
        res = Response(trace.trace, cond, meta)
        debug.enter()

class ExportMenubar(object):
    def __init__(self, maingui):
        self.maingui = maingui
    def copy_response_values_to_clipboard(self):
        try:
            response = self.maingui.tiffFig.responseFig.response
            clip = '\t'.join(map(str, [
                response.OSI,
                response.DSI,
                response.CV,
                response.sigma,
                response.Opref,
                response.Rmax,
                response.residual
            ]))
            cboard = QApplication.clipboard()
            cboard.clear(mode=cboard.Clipboard)
            cboard.setText(clip, mode=cboard.Clipboard)
        except Exception as e:
            QMessageBox.information(self.maingui,
                'Exporting...',
                'Could not find response values.',
                QMessageBox.Ok)
        # else:
        #     QMessageBox.information(self.maingui,
        #         'Exporting...',
        #         'Response values are copied to clipboard.',
        #         QMessageBox.Ok)

    def copy_response_matrix_to_clipboard(self):
        try:
            matrix = self.maingui.tiffFig.responseFig.response.matrix
            header, bodycols = zip(*matrix)
            table = [header] + zip(*bodycols)
            clip = '\n'.join(
                '\t'.join(map(str, row)) for row in table
            )
            cboard = QApplication.clipboard()
            cboard.clear(mode=cboard.Clipboard)
            cboard.setText(clip, mode=cboard.Clipboard)
        except Exception as e:
            QMessageBox.information(self.maingui,
                'Exporting...',
                'Could not find response values.',
                QMessageBox.Ok)
        # else:
        #     QMessageBox.information(self.maingui,
        #         'Exporting...',
        #         'Response values are copied to clipboard.',
        #         QMessageBox.Ok)

#     def copy_response_values_to_clipboard(self):
#         try:
#             response = self.maingui.tiffFig.responseFig.response
#             clip = '\t'.join(map(str, [
#                 response.OSI,
#                 response.DSI,
#                 response.CV,
#                 response.sigma,
#                 response.Opref,
#                 response.Rmax,
#                 response.residual
#             ]))
#             cboard = QApplication.clipboard()
#             cboard.clear(mode=cboard.Clipboard)
#             cboard.setText(clip, mode=cboard.Clipboard)
#         except Exception as e:
#             QMessageBox.information(self.maingui,
#                 'Exporting...',
#                 'Could not find response values.',
#                 QMessageBox.Ok)
#         else:
#             QMessageBox.information(self.maingui,
#                 'Exporting...',
#                 'Response values are copied to clipboard.',
#                 QMessageBox.Ok)
