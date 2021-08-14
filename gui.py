import sys
from PyQt5 import QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextBrowser, QComboBox, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QTableWidget
from tutorial.spiders.search_spider import SearchSpider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from multiprocessing import Process, Manager, freeze_support
from datetime import datetime
from scrapy.crawler import CrawlerProcess
import json
def crawl(Q, keyword):
  # CrawlerProcess
  process = CrawlerProcess()

  process.crawl(SearchSpider, Q=Q, keyword=keyword)
  process.start()

  # CrawlerRunner
  """runner = CrawlerRunner(settings={
      'USER_AGENT': ua,
      'ROBOTSTXT_OBEY': is_obey
  })
  d = runner.crawl(BookSpider, Q=Q)
  d.addBoth(lambda _: reactor.stop())
  reactor.run()"""

class UI(QWidget):
  def __init__(self):
    super(UI, self).__init__()
    self.setWindowTitle('Scrapy')
    self.keyword_line = QLineEdit(self)
    self.crawl_btn = QPushButton('Start', self)
    self.h_layout = QHBoxLayout()
    self.log_browser = QTextBrowser(self)
    self.table_widget = QTableWidget(0, 5)
    self.table_widget.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
    self.table_widget.setHorizontalHeaderItem(1, QTableWidgetItem("Link"))
    self.table_widget.setHorizontalHeaderItem(2, QTableWidgetItem("Price"))
    self.table_widget.setHorizontalHeaderItem(3, QTableWidgetItem("Image"))
    self.table_widget.setHorizontalHeaderItem(4, QTableWidgetItem("Time"))

    self.h_layout.addWidget(QLabel('Keyword'))
    self.h_layout.addWidget(self.keyword_line)
    self.v_layout = QVBoxLayout()
    self.v_layout.addLayout(self.h_layout)
    self.v_layout.addWidget(self.table_widget, 4)
    self.v_layout.addWidget(self.log_browser, 1)
    self.v_layout.addWidget(self.crawl_btn)
    self.setLayout(self.v_layout)
    self.resize(800, 600)

    self.Q = Manager().Queue()
    self.log_thread = LogThread(self)
    self.crawl_btn.clicked.connect(self.crawl_slot)
  
  def crawl_slot(self):
    if (self.crawl_btn.text() == 'Start'):
      self.crawl_btn.setText('Stop')
      self.log_thread.start()
      self.start_process()
    else:
      self.crawl_btn.setText('Start')
      self.p.terminate()
      self.log_thread.terminate()
      now = datetime.now()
      current_time = now.strftime("%H:%M:%S")
      self.log_browser.append('Service Stopped {}\n'.format(current_time))
  def start_process(self):
    keyword = self.keyword_line.text().strip()
    self.p = Process(target=crawl, args=(self.Q, keyword))
    self.p.start()
class LogThread(QThread):
    firstScan = True
    oldItems = []
    def __init__(self, gui):
      super(LogThread, self).__init__()
      self.gui = gui
    def run(self):
      while True:
        if not self.gui.Q.empty():
          pr = self.gui.Q.get()
          now = datetime.now()
          current_time = now.strftime("%H:%M:%S")
          if pr == 'Start':
            self.gui.log_browser.append('Service Started {}\n'.format(current_time))
          elif pr == 'Stop':
            self.gui.log_browser.append('Service Stopped {}\n'.format(current_time))
          elif pr == 'Scrapped':
            self.gui.log_browser.append('Scrapped {}\n'.format(current_time))
            self.firstScan = False
          else:
            obj = json.loads(pr)
            if self.firstScan == True:
              self.oldItems.append(obj)
            else:
              exist = False
              for oi in self.oldItems:
                if oi['link'] == obj['link']:
                  exist = True
              if exist != True:
                self.gui.table_widget.insertRow(0)
                self.gui.table_widget.setItem(0, 0, QTableWidgetItem(obj['name']))
                self.gui.table_widget.setItem(0, 1, QTableWidgetItem(obj['link']))
                self.gui.table_widget.setItem(0, 2, QTableWidgetItem(obj['price']))
                self.gui.table_widget.setItem(0, 3, QTableWidgetItem(obj['image']))
                self.gui.table_widget.setItem(0, 4, QTableWidgetItem(current_time))
                self.oldItems.append(obj)
          self.gui.log_browser.moveCursor(QtGui.QTextCursor.End)
          self.msleep(10)
if __name__ == '__main__':
  freeze_support()
  app = QApplication(sys.argv)
  ui = UI()
  ui.show()
  sys.exit(app.exec_())