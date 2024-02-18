import sys
from PyQt5.QtWidgets import QTextEdit, QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, QLabel, QHBoxLayout
from PyQt5.QtCore import QSettings
from io import StringIO
from get_picture import spider
import json


def save_settings(settings_dict):
	settings_str = json.dumps(settings_dict)
	settings = QSettings('yzrmint', '下载图片')
	settings.setValue('settingsKey', settings_str)

def load_settings():
	default = '{"text": "", "driver_path": "", "download_dir": ""}'
	settings = QSettings('yzrmint', '下载图片')
	settings_str = settings.value('settingsKey', defaultValue=default)
	settings_dict = json.loads(settings_str)
	return settings_dict

output=sys.stdout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt

class FileDragDropWidget(QLineEdit):
	def __init__(self, describe="拖动文件到这里或者点击选择文件", lastInput="", parent=None):
		super(FileDragDropWidget, self).__init__(parent)
		self.input = lastInput  # 新增的参数来控制行为
		self.describe = describe
		self.setDragEnabled(True)
		self.setPlaceholderText(self.describe)		
		# 根据 input 参数决定是显示占位符还是直接显示 describe 文本
		if self.input:
			self.setText(self.input)
			

	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls():
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		files = [url.toLocalFile() for url in e.mimeData().urls()]
		if files:
			self.setText(files[0])  # 只取第一个文件
			# 如果 input 为 True，将会使用实际输入替换 describe
			if self.input:
				self.describe = files[0]
				
	def clearText(self):
		self.setText('')			


class App(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
		

	def initUI(self):
		self.setWindowTitle('下载图片')
		self.setGeometry(500, 500, 500, 300)
		self.layout = QVBoxLayout()	
		lastInput = load_settings()
		self.filePaths = [FileDragDropWidget("完整url，或粘贴整个消息", lastInput["text"]), 
					FileDragDropWidget("把驱动exe拖入这里", lastInput["driver_path"]), 
					FileDragDropWidget("输出文件夹路径（可拖入）", lastInput["download_dir"])
					]

		for filePath in self.filePaths:
			self.layout.addWidget(filePath)

		label1 = QLabel("适用于Edge<br> \
				驱动下载地址：<br> \
				<a href='https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver'>https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver</a> <br> <br> \
				运行时可能会显示为无响应，这是正常情况。请等待\"执行完毕\"窗口跳出后再操作<br>")
		label1.setOpenExternalLinks(True)
		self.layout.addWidget(label1)

		self.outputTextBox = QTextEdit(self)
		self.outputTextBox.setReadOnly(True)  # 设置为只读模式
		self.outputTextBox.setFixedHeight(100)  # 可以根据需要调整高度
		self.layout.addWidget(self.outputTextBox)
		
		self.hbox = QHBoxLayout()
		self.runButton = QPushButton('运行')
		self.runButton.clicked.connect(self.runFunction)
		self.hbox.addWidget(self.runButton)
		self.cleanButton = QPushButton('清除历史记录')
		self.cleanButton.clicked.connect(self.cleanHistory)
		self.hbox.addWidget(self.cleanButton)
		self.layout.addLayout(self.hbox)

		self.setLayout(self.layout)

	def runFunction(self):
		args = [filePath.text() for filePath in self.filePaths if filePath.text()]
		output_stream = StringIO()
		sys.stdout = output_stream
		try:
			spider(*args)  # 使用解包操作符调用函数，适应不定数量的参数
			output_content = output_stream.getvalue()
			self.outputTextBox.append(output_content)
			QMessageBox.information(self, "成功", "执行完毕！")
			save_settings({
				"text": args[0],
				"driver_path": args[1],
				"download_dir": args[2],
			})
		except Exception as e:
			QMessageBox.critical(self, "错误", f"执行出错: {str(e)}")
		output_stream.close()

	def cleanHistory(self):
		save_settings({"text": "", "driver_path": "", "download_dir": ""})
		for filePath in self.filePaths:
			filePath.clearText()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	ex.show()
	sys.exit(app.exec_())
