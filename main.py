import sys
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextBrowser, QComboBox, QHBoxLayout, QVBoxLayout, QTableWidgetItem, QTableWidget
from tutorial.spiders.search_spider import SearchSpider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from multiprocessing import Process, Manager
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
    # self.log_browser = QTextBrowser(self)
    self.table_widget = QTableWidget(0, 4)
    self.table_widget.setHorizontalHeaderItem(0, QTableWidgetItem("Name"))
    self.table_widget.setHorizontalHeaderItem(1, QTableWidgetItem("Link"))
    self.table_widget.setHorizontalHeaderItem(2, QTableWidgetItem("Price"))
    self.table_widget.setHorizontalHeaderItem(3, QTableWidgetItem("Image"))

    self.h_layout.addWidget(QLabel('Keyword'))
    self.h_layout.addWidget(self.keyword_line)
    self.v_layout = QVBoxLayout()
    self.v_layout.addLayout(self.h_layout)
    self.v_layout.addWidget(self.table_widget)
    self.v_layout.addWidget(self.crawl_btn)
    self.setLayout(self.v_layout)

    self.Q = Manager().Queue()
    self.log_thread = LogThread(self)
    self.crawl_btn.clicked.connect(self.crawl_slot)
  
  def crawl_slot(self):
    if (self.crawl_btn.text() == 'Start'):
      self.crawl_btn.setText('Stop')
      keyword = self.keyword_line.text().strip()
      self.p = Process(target=crawl, args=(self.Q, keyword))
      self.p.start()
      self.log_thread.start()
    else:
      self.crawl_btn.setText('Start')
      self.p.terminate()
      self.log_thread.terminate()
class LogThread(QThread):
    def __init__(self, gui):
      super(LogThread, self).__init__()
      self.gui = gui
      self.items = []
 
    def run(self):
      while True:
        if not self.gui.Q.empty():
          pr = self.gui.Q.get()
          if pr != 'Start' and pr != 'Stop':
            exist = False
            obj = json.loads(pr)
            for item in self.items:
              if item['link'] == obj['link']:
                exist = True
            if exist != True:
              self.items.append(obj)
              row = len(self.items)
              self.gui.table_widget.setRowCount(row)
              self.gui.table_widget.setItem(row - 1, 0, QTableWidgetItem(obj['name']))
              self.gui.table_widget.setItem(row - 1, 1, QTableWidgetItem(obj['link']))
              self.gui.table_widget.setItem(row - 1, 2, QTableWidgetItem(obj['price']))
              self.gui.table_widget.setItem(row - 1, 3, QTableWidgetItem(obj['image']))

          self.msleep(10)
if __name__ == '__main__':
  app = QApplication(sys.argv)
  ui = UI()
  ui.show()
  sys.exit(app.exec_())