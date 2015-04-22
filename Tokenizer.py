import re
from os.path import exists
import os 

#The idea is to build a automaton to identify the Tokens 
# And to implantion using the state and action table 

class Tokenizer:
	KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int",
				"char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if",
				"else", "while", "return"]
	
	#			0		 1			  2				3		         4		 5		   	6
	TOKENS = ["NULL","keyword", "identifier", "integerConstant", "symbol", "NULL", "stringConstant" ]
	               #   C   _   D  Sy   "   $   Other
	state_table = [ [  1,  2,  3,  4,  5,  0, -1], # 0
					[  1,  2,  2, -1, -1, -1, -1], # 1 
					[  2,  2,  2, -1, -1, -1, -1], # 2 
					[ -1, -1,  3, -1, -1, -1, -1], # 3 
					[ -1, -1, -1, -1, -1, -1, -1], # 4 
					[  5,  5,  5,  5,  6,  5,  5], # 5
					[ -1, -1, -1, -1, -1, -1, -1] ] # 6
	
				   # ERROR = 0; MACHINE_ACCEPT = 1; HALT_RETURN = 2
				   #   C   _   D  Sy   "   $   Other
	action_table =[ [  1,  1,  1,  1,  1,  1,  0], # 0
					[  1,  1,  1,  2,  2,  2,  2], # 1 
					[  1,  1,  1,  2,  2,  2,  2], # 2 
					[  2,  2,  1,  2,  2,  2,  2], # 3 
					[  2,  2,  2,  2,  2,  2,  2], # 4 
					[  1,  1,  1,  1,  1,  1,  1], # 5
					[  2,  2,  2,  2,  2,  2,  2]] # 6

	SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']


	# alphabet of the DFA 
	CHAR = 0 
	UNDERSCORE = 1
	DIGIT = 2
	SY = 3
	QUOTATION = 4
	SPACE = 5
	OUTHER = 6



	def __init__(self,inputFileDirPath,fileName):
		inputFileFullPath = os.path.join(inputFileDirPath,fileName)
		self.inputFile = open(inputFileFullPath)
		outputFilePath = re.sub('.jack','T.xml',inputFileFullPath)
		self.outputFile = open(outputFilePath,'w')
		self.commentsRemoved = ""
		self.counterLine = 0
		self.initialize() 

	def initialize(self):
		# removed the comment and give us string of code (self.commentRemoved)
		fileContents = self.inputFile.read()
		currentIndex = 0
		quoteMode = False
		#Loop to strip comments.  Note that if a file has a beginning comment indicator (// or /*) 
		#as the last characters this won't remove them.
		while currentIndex < len(fileContents) - 1:
			if fileContents[currentIndex] == "\"":
				quoteMode = not quoteMode
				self.commentsRemoved += fileContents[currentIndex]
				currentIndex += 1
			elif (not quoteMode) and fileContents[currentIndex] == "/" and fileContents[currentIndex + 1] == "/": 
				currentIndex = fileContents.find("\n", currentIndex + 1)
			elif (not quoteMode) and fileContents[currentIndex] == "/" and fileContents[currentIndex + 1] == "*":
				currentIndex = fileContents.find("*/", currentIndex + 1) + 2
			else:
				self.commentsRemoved += fileContents[currentIndex]
				currentIndex += 1
		self.commentsRemoved += fileContents[currentIndex]
		self.commentsRemoved = re.sub('[\n|\t]',' ',self.commentsRemoved).strip()
		#self.commentsRemoved = re.sub('[ ]+',' ',self.commentsRemoved) 
		self.commentsRemoved += ' '

	def isSymbol(self,char):
		for item in Tokenizer.SYMBOLS:
			if (item == char):
				return 1
		return 0

	def whoAmI(self,char):
		if (char == ' '):
			return Tokenizer.SPACE
		elif (char == '_'):
			return Tokenizer.UNDERSCORE
		elif (char == '"'):
			return Tokenizer.QUOTATION
		elif ( ( ord(char) > 47 ) and ( ord(char) < 58 ) ):
			return Tokenizer.DIGIT
		elif ( ( ( ord(char) > 64 ) and ( ord(char) < 91 ) ) or ( ( ord(char) > 96 ) and ( ord(char) < 123 ) ) ):
			return Tokenizer.CHAR
		elif (self.isSymbol(char)):
			return Tokenizer.SY
		else : 
			return Tokenizer.OUTHER


	def keywordChack(self,word):
		for item in Tokenizer.KEYWORDS:
			if (word == item):
				return 1
		return 2

	def changeWordToXml(self,word):
		if (word == '<'):
			return "&lt;"
		if (word == '>'):
			return "&gt;"
		if (word == '"'):
			return "&quot;"
		if (word == '&'):
			return "&amp;"
		return word


	def writeToken(self,token,word):
		#self.counterLine += 1
		word = word.replace('"',"")
		if (token == 1):
			token = self.keywordChack(word)
		if (token == 4):
			word = self.changeWordToXml(word)
		self.outputFile.write("<" + Tokenizer.TOKENS[token] + "> " + word + " </" + Tokenizer.TOKENS[token] + ">\n")
		

	def token(self):
		#using at the state and action table to get the token 
		index = 0
		currentState = 0 
		currentWord = ""
		self.outputFile.write("<tokens>\n")
		while (index < len(self.commentsRemoved)):
			char = self.whoAmI(self.commentsRemoved[index])
			action = Tokenizer.action_table[currentState][char]
			if action == 1:
				currentState = Tokenizer.state_table[currentState][char]
				if (not (currentState == 0)):
					currentWord += self.commentsRemoved[index]
				index += 1
			if action == 2:
				self.writeToken(currentState,currentWord)
				currentState = 0
				currentWord = ""
		self.outputFile.write("</tokens>\n")

