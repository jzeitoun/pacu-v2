from PyQt4.QtGui import (QTableWidget, QTableWidgetItem,
                         QPushButton, QCheckBox, QHBoxLayout, QWidget)
from PyQt4.QtCore import QString, QRect, Qt

from ext.console import debug
from ext.model.session import s
from ext.model.analysis import Analysis
from ext.roi_table.controller import ROITableController

# table.cellClicked.connect(cellclicked)
def cellclicked(row, column):
    print "Row %d and Column %d was clicked" % (row, column)
    # item = self.table.itemAt(row, column)
    # self.ID = item.text() kwargs
    # debug.enter()

def make_widget(main, show=True):

    id = main.persistant['id']
    table = QTableWidget()
    table.controller = ROITableController(table, main)
    table.setGeometry(QRect(20, 33, 496, 296))
    table.setWindowTitle('ceilingfaan - ROI Table - Work in progress')
    analysis = s.query(Analysis).order_by(Analysis.date.desc()).all()
    table.setRowCount(len(analysis))
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(
        QString('CONTROL,DATE,MOUSE,FILENAME').split(','))

    current_analysis = None
    on_render = table.controller.on('render')
    on_import = table.controller.on('import')
    for nrow, entity in enumerate(analysis):
        if entity.id == id:
            print 'Found matching analysis data', id, 'at nrow:', nrow
            current_analysis = entity
            current_nrow = nrow
            continue

        for ncol, attr in enumerate('date mouse_id filename'.split()):
            field = getattr(entity, attr)
            item = QTableWidgetItem(str(field))
            item.setFlags(Qt.ItemIsEnabled)
            table.setItem(nrow, ncol + 1, item)

        render_btn = QPushButton('Render', checkable=True)
        render_btn.setStyleSheet('font-size: 9px; background-color: skyblue;')
        import_btn = QPushButton('Import')
        import_btn.setStyleSheet('font-size: 9px;')

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(5, 0, 5, 0)
        btn_layout.addWidget(render_btn)
        btn_layout.addWidget(import_btn)

        btn_widget = QWidget()
        btn_widget.nrow = nrow
        btn_widget.analysis_id = entity.id
        btn_widget.ext_roi_set = None
        btn_widget.setLayout(btn_layout)
        table.setCellWidget(nrow, 0, btn_widget)

        render_btn.clicked.connect(on_render)
        import_btn.clicked.connect(on_import)

    if current_analysis:
        table.removeRow(current_nrow)
        table.insertRow(0)
        item = QTableWidgetItem('Current Analysis')
        item.setFlags(Qt.ItemIsEnabled)
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(0, 0, item)
        for ncol, attr in enumerate('date mouse_id filename'.split()):
            field = getattr(current_analysis, attr)
            item = QTableWidgetItem(str(field))
            item.setFlags(Qt.ItemIsEnabled)
            table.setItem(0, ncol + 1, item)
        # debug.enter()

    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.NoSelection)
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)

    if show: table.show()

    return table
