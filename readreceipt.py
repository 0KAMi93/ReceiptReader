import cv2
import pytesseract
import re, csv

shops = [
		"tesco", 
		"sainsburys",
		"waitrose", 
		"aldi",
		"peacocks"
		]

# Uses Tesseract and cv2 to read text from image of receipt
def readReceipt():
	img = cv2.imread('test4.jpg')
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (3,3), 0)
	thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
	invert = 255 - opening
	receipt_data = pytesseract.image_to_string(invert, lang='eng') # PSM 4 seems to be the best for receipts...
	return receipt_data

# Reads converted receipt text and searches for a known shop
def shopCheck(text):
	result = "Not in list"
	for i in shops:
		x = re.search(i, text, re.IGNORECASE)
		if x:
			result = i
	if result == "Not in list":
		print("[-] Unknown Receipt")
		exit()
	return result

# Converts string to lists based on newlines
def formatData(data):
	out = []
	buff = []
	for c in data:
		if c == "\n":
			out.append(''.join(buff))
			buff = []
		else:
			buff.append(c)
	else:
		if buff:
			out.append(''.join(buff))
	return out

# Create lists of relevant data for each specific shop - As receipts will differ
def tescoReceipt(formatted_data):
	shopitems = []
	for i in formatted_data:
		if '£' in i:
			if 'TOTAL' in i:
				total = i
				total = total.replace(" ", "")
				total = re.findall(r"(?:[\£\$\€]{1}[,\d]+.?\d*)",total)
				break
			else:
				shopitems.append(i)
	itemqty = []
	itemname = []
	itemprice = []
	for n in shopitems:
		qty = n[0]
		n = n.replace(qty, '', 1)
		n = n.lstrip()
		price = re.findall(r"(?:[\£\$\€]{1}[,\d]+.?\d*)",n)
		n = n.replace(price[0], '')
		n = n.rstrip()
		# Add to lists
		itemqty.append(qty)
		itemname.append(n)
		itemprice.append(price[0])
	array = [itemqty,itemname,itemprice, total]
	return array
	
def peacocksReceipt(formatted_data):
	shopitems = []
	for i in formatted_data:
		if '£' in i:
			if 'Total:' in i:
				total = i
				total = total.replace(" ", "")
				total = re.findall(r"(?:[\£\$\€]{1}[,\d]+.?\d*)",total)
				break
			else:
				shopitems.append(i)
	itemqty = []
	itemname = []
	itemprice = []
	for n in shopitems:
		if n[0].isnumeric():
			qty = n[0]
		else:
			qty = 1
		price = re.findall(r"(?:[\£\$\€]{1}[,\d]+.?\d*)",n)
		n = n.replace(price[0], '')
		n = n.rstrip()
		# Add to lists
		itemqty.append(qty)
		itemname.append(n)
		itemprice.append(price[0])
	array = [itemqty,itemname,itemprice, total]
	return array

# Output to CSV
def output(file_name, array):
	receipt_array = array
	file = open(file_name, 'w')
	writer = csv.writer(file)
	writer.writerow([
			"Quantity",
			"Item Name",
			"Price"])
	for i in range(len(receipt_array[0])):
		writer.writerow([
			receipt_array[0][i],
			receipt_array[1][i],
			receipt_array[2][i]
			])
	writer.writerow([
		"Total",
		"",
		receipt_array[3][0]
	])
	file.close()

t = readReceipt()
l = formatData(t)


if shopCheck(t) == 'tesco':
	output("Tesco_Receipt.csv",tescoReceipt(l))
elif shopCheck(t) == 'peacocks':
	output("Peacocks_Receipt.csv",peacocksReceipt(l))
else:
	print("[-] Found  Receipt")
