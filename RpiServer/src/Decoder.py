class Decoder:

	def decode(path):
		formatString = path.split("/")[1]
		if(len(formatString)>0):
			if(formatString.find('?')!=-1):
				[function, arguments] = formatString.split("?")
				argList = []
				for arg in arguments.split("&"):
					argList.append(arg.split("="))
			else:
				function = formatString
				argList = None	
			return function, argList
		

	def fun(x, y):
		return int(x)+int(y)



if __name__ == '__main__':
	function, argList = Decoder.decode(input())
	print('function=' + function)
	print('arguments=' + str(argList))
	if(hasattr(Decoder, function)):
		print(getattr(Decoder, function)(*tuple([val[1] for val in argList])))
	else:
		print('No such function')
