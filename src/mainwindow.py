import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QMessageBox
from src.camerasection import CameraSection
from src.camera import Camera
from src.manualmovement import ManualMovementSection
from src.motorbackend import DaisyDriver
from serial.serialutil import SerialException

class MainWindow(QWidget):
	
	def __init__(self):
		super().__init__()
		
		# get customised PiCamera instance
		self.camera = Camera()
		
		# get daisy driver object, disable manual movement section if not available
		try: 
			self.DD = DaisyDriver()
			self.DDconnected = True
		except SerialException:
			self.DDconnected = False
			self.DD = DaisyDriver(connected=False)
			
		# initialise user interface
		self.initUI()
		
	def initUI(self):
		# general settings
		self.setWindowTitle('DaisyLiteGUI v1.0')
		
		# main layout
		mainlayout = QHBoxLayout()
		
		# get widgets
		self.camerasection = CameraSection(self, self.camera)
		self.manualmovement = ManualMovementSection(self, self.camera, self.DD)
		
		# add widgets to main layout
		mainlayout.addWidget(self.camerasection)
		mainlayout.addWidget(self.manualmovement)
		
		# check if DD plugged in, disable manual movement section if so
		# and display warning
		if not self.DDconnected:
			self.manualmovement.setEnabled(False)
			warning_dialog = QMessageBox.warning(self, 'DaisyDriver Warning', 
									'Warning: No DaisyDriver Detected.', QMessageBox.Ok)
			
		# set mainlayout as widget layout
		self.setLayout(mainlayout)
		
		# set window geometry
		self.setFixedSize(mainlayout.sizeHint())
		self.move(0, 0)
		
	def closeEvent(self, event):
		# check if timer is running, show warning box if so
		try:
			if self.camera.maintimer._timer.isAlive():
				exit_question = QMessageBox.question(self, 'Camera Timer Warning', 
									'Camera timer still running, are you sure you want to exit?', 
									QMessageBox.Cancel | QMessageBox.Yes, QMessageBox.Yes)
					
				if exit_question == QMessageBox.Yes:
					self.camera.stop_timed_capture()
					# ensure preview thread ends
					self.camera.preview_state = False
					# ensure close daisy driver serial object (if open)
					try:
						self.DD.close()
					except AttributeError:
						pass
						
					event.accept()
				elif exit_question == QMessageBox.Cancel:
					event.ignore()
					
		# in case no timer thread has been created (start button never pressed) 
		except AttributeError:
			# ensure preview thread ends
			self.camera.preview_state = False
			# ensure close daisy driver serial object (if open)
			try:
				self.DD.close()
			except AttributeError:
				pass
				
			pass
			
def run():
	
    app = QApplication(sys.argv)

    main = MainWindow()
    
    main.show()

    sys.exit(app.exec_())

