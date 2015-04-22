from Tokenizer import Tokenizer
from os.path import exists
import os 

inputFile = r"A:\program_language\tr10\ArrayTest"


for currentFile in os.listdir(inputFile):
	if os.path.splitext(currentFile)[1] == '.jack':
		temp = Tokenizer(inputFile,currentFile)
		temp.token()
