import sys
import os
import glob
import tkinter as tk
from tkinter import filedialog 
import tkinter.scrolledtext as tkscrolled
import syglass
from syglass import pyglass
#import code

class Application(tk.Frame):
	prev_in, prev_out = " ", " "
	config = {}
	setInput = 1
	setOutput = 1
	if(os.path.isfile('config.ini')):
		with open('config.ini', 'r') as f:
			lines = f.readlines()
			print(lines)
			config['out'] = lines[0][:-1]
			config['in'] = lines[1]
	if 'out' in config:
		prev_out = config['out']
		setOutput = 0
	if 'in' in config:
		prev_in = config['in']
		setInput = 0
	outputFoldername = prev_out
	inputFoldername = prev_in
	screenMessages = []
	print(config)

	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		master.geometry("500x250")
		master.title("syGlass AutoCreator -- Image Folders to syGlass Projects")
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.input = tk.Button(self)
		self.input["text"] = "Input Folder: " + self.inputFoldername
		self.input["width"] = 400
		self.input["command"] = self.inputBrowseFiles
		self.input.pack(side="top") 
		
		self.output = tk.Button(self)
		self.output["width"] = 400
		self.output["text"] = "Output Folder: " + self.outputFoldername
		self.output["command"] = self.outputBrowseFiles
		self.output.pack(side="top") 
		
		self.textbox = tkscrolled.ScrolledText(self, height=10, width=70)
		self.textbox.pack(side="top")
		self.textbox['state'] = 'disabled'
		self.textbox['foreground'] = 'white'
		self.textbox['background'] = 'black'
		self.addTextLine('Choose your input and output directories and press convert.')

		self.convert = tk.Button(self, text="CONVERT", fg="red", command=self.convert)
		self.convert.pack(side="bottom")

	def outputBrowseFiles(self): 
		self.outputFoldername = filedialog.askdirectory(initialdir = self.inputFoldername, title = "Select a Folder") 
		self.output["text"] = "Output Folder: " + self.outputFoldername
		self.config['out'] = self.outputFoldername
		self.setOutput = 0
	
	def inputBrowseFiles(self): 
		self.inputFoldername = filedialog.askdirectory(initialdir = self.outputFoldername, title = "Select a Folder") 
		self.input["text"] = "Input Folder: " + self.inputFoldername
		self.config['in'] = self.inputFoldername
		self.setInput = 0
		
	def addTextLine(self, text):
		self.textbox['state'] = 'normal'
		self.textbox.insert(tk.END, text+"\n")
		self.textbox['state'] = 'disabled'
		self.textbox.see("end")
		self.update()

	def convert(self):
		inputFoldername = self.inputFoldername
		outputFoldername = self.outputFoldername
		print(self.setInput)
		print(self.setOutput)
		if self.setInput or self.setOutput:
			self.addTextLine("Set Input and Output folders first.")
			return
		dirs = []
		all = os.listdir(inputFoldername)
		successfulProjects = []
		for each in all:
			fullpath = os.path.join(inputFoldername, each)
			
			if os.path.isdir(fullpath):
				l = glob.glob(os.path.join(fullpath, "*.png"))
				l.append(glob.glob(os.path.join(fullpath, "*.tif*")))
				l.append(glob.glob(os.path.join(fullpath, "*.dicom")))
				l.append(glob.glob(os.path.join(fullpath, "*.jpeg")))
				l.append(glob.glob(os.path.join(fullpath, "*.jpg")))
				
				if len(l) > 0:
					dirs.append(fullpath)
					
		if not os.path.exists(outputFoldername):
			os.makedirs(outputFoldername)
			
		for imagesetFullPath in dirs:
			basename = os.path.basename(imagesetFullPath)
			msg = "Found directory: " + basename
			self.addTextLine(msg)
			newPath = os.path.join(outputFoldername, basename)
			self.addTextLine("Creating...")
			if os.path.exists(newPath):
				self.addTextLine("Project found already in Output Folder, skipping...")
				continue
			try:
				project = pyglass.CreateProject(pyglass.path(outputFoldername), basename)
				dd = pyglass.DirectoryDescription()
				firstPNG = glob.glob(os.path.join(imagesetFullPath, "*.png"))[0]
				firstPNG = firstPNG.replace("\\", "/")
				dd.InspectByReferenceFile(firstPNG)
				dataProvider = pyglass.OpenPNGs(dd.GetFileList())
				cd = pyglass.ConversionDriver()
				
				cd.SetInput(dataProvider)
				cd.SetOutput(project)
				cd.StartAsynchronous()
				lowPercentage = 0
				print(cd.GetPercentage())
				while cd.GetPercentage() < 100:
					if cd.GetPercentage() > (lowPercentage + 10):
						lowPercentage = cd.GetPercentage()
						self.addTextLine("Progress: " + str(cd.GetPercentage())[0:4] + "%")
			except Exception as e:
				self.addTextLine("Something went wrong...")
				self.addTextLine(str(e))
			else:
				self.addTextLine("Success...!")
				successfulProjects.append(newPath)
				
		#afterward, use pyglass::VolumeLibrary to reload, Call VolumeLibrary::ReloadLibrary(), Call VolumeLibrary::PutEntry()
		pv = pyglass.VolumeLibrary()
		pv.ReloadLibrary()

		self.addTextLine("------------------------------")
		self.addTextLine("Successfully created " + str(len(successfulProjects)) + " / " + str(len(dirs)))
		lines = []
		lines.append(self.config['out'] + "\n")
		lines.append(self.config['in'])
		with open('config.ini', 'w') as f:
			f.writelines(lines)
			
def main(args):
	print("Batch Project Creator, by Michael Morehead")
	print("Accepts a folder containing folders of images")
	print("Creates a syGlass Project for each subfolder, with the folder name as the Project name.")
	print("---------------------------------------")
	print("Usage: Launch and follow the built-in GUI.")
	print("---------------------------------------")
	root = tk.Tk()
	ex = Application(root)
	root.mainloop()
	

