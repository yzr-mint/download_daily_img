import sys
from PyQt5.QtWidgets import QTextEdit, QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, QLabel
from io import StringIO
from get_picture import spider

output=sys.stdout
class FileDragDropWidget(QLineEdit):
	def __init__(self, describe = "拖动文件到这里或者点击选择文件", parent=None):
		super(FileDragDropWidget, self).__init__(parent)
		self.setDragEnabled(True)
		self.setPlaceholderText(describe)
	
	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls():
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		files = [url.toLocalFile() for url in e.mimeData().urls()]
		if files:
			self.setText(files[0])  # 只取第一个文件

class App(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setWindowTitle('下载图片')
		self.setGeometry(500, 500, 500, 300)

		self.layout = QVBoxLayout()

		self.filePaths = [FileDragDropWidget("完整url，或粘贴整个消息"), 
					FileDragDropWidget("把驱动exe拖入这里"), 
					FileDragDropWidget("输出文件夹路径（可拖入）")
					]
		for filePath in self.filePaths:
			self.layout.addWidget(filePath)

		label1 = QLabel("适用于Edge<br> \
                驱动下载地址：<br> \
                <a href='https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver'>https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver</a> <br> <br> \
				运行时可能会显示为无响应，这是正常情况。请等待\"执行完毕\"窗口跳出后再操作<br> \ ")
		label1.setOpenExternalLinks(True)
		self.layout.addWidget(label1)

		self.outputTextBox = QTextEdit(self)
		self.outputTextBox.setReadOnly(True)  # 设置为只读模式
		self.outputTextBox.setFixedHeight(100)  # 可以根据需要调整高度
		self.layout.addWidget(self.outputTextBox)


		self.runButton = QPushButton('运行')
		self.runButton.clicked.connect(self.runFunction)
		self.layout.addWidget(self.runButton)

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
		except Exception as e:
			QMessageBox.critical(self, "错误", f"执行出错: {str(e)}")
		output_stream.close()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	ex.show()
	sys.exit(app.exec_())
