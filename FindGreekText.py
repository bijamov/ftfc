import os
import re

GR_LIST=['ς','ε','ρ','τ','υ','θ','ι','ο','π','α','σ','δ','φ','γ','η','ξ','κ','λ','ζ','χ','ψ','ω','β','ν','μ','ς','Ε','Ρ','Τ','Υ','Θ','Ι','Ο','Π','Α','Σ','Δ','Φ','Γ','Η','Ξ','Κ','Λ','Ζ','Χ','Ψ','Ω','Β','Ν','Μ','Ά','Έ','Ύ','Ί','Ό','Ή','Ώ','Ϊ','Ϋ','έ','ύ','ί','ό','ά','ή','ώ','ϊ','ϋ'];
HTML_S_LIST=['<!DOCTYPE','<a','<abbr','<acronym','<address','<applet','<area','<article','<aside','<audio','<b','<base','<basefont','<bdi','<bdo','<big','<blockquote','<body','<br','<button','<canvas','<caption','<center','<cite','<code','<col','<colgroup','<data','<datalist','<dd','<del','<details','<dfn','<dialog','<dir','<div','<dl','<dt','<em','<embed','<fieldset','<figcaption','<figure','<font','<footer','<form','<frame','<frameset','<h1','<h2','<h3','<h4','<h5','<h6','<head','<header','<hr','<html','<i','<iframe','<img','<input','<ins','<kbd','<label','<legend','<li','<link','<main','<map','<mark','<meta','<meter','<nav','<noframes','<noscript','<object','<ol','<optgroup','<option','<output','<p','<param','<picture','<pre','<progress','<q','<rp','<rt','<ruby','<s','<samp','<section','<select','<small','<source','<span','<strike','<strong','<style','<sub','<summary','<sup','<svg','<table','<tbody','<td','<template','<textarea','<tfoot','<th','<thead','<time','<title','<tr','<track','<tt','<u','<ul','<var','<video','<wbr']
export_array = []
check_table = []
pointer_line = 0
pointer_char = -1
mode = 0 # [0 None] - [1 HTML OUTSIDE] - [2 HTML INSIDE] - [3 PHP] - [4 XML] - [13 HTML outside Μεσα σε PHP] - [23 HTML inside Μεσα σε PHP]
export_string = ''
pointer_mode = [0,0]


def GetChar_next(): # Περπατάει μπροστά ενα γράμμα.
	global pointer_char
	global pointer_line
	global file
	lines = len(file) - 1 
	pointers = len(file[pointer_line]) - 1
	if pointers > pointer_char:
		pointer_char = pointer_char + 1
	elif lines > pointer_line:
		pointer_line = pointer_line + 1
		pointer_char = 0
	else:
		return None
	return file[pointer_line][pointer_char]

def GetChar_previous(): # Περπατάει πίσω ενα γράμμα.
	global pointer_char
	global pointer_line
	global file

	if pointer_char != 0:
		pointer_char = pointer_char - 1
		return
	if pointer_line != 0:
		pointer_line = pointer_line - 1
		pointer_char = len(file[pointer_line]) -1
		return
	pointer_line = 0
	pointer_char = 0
	return file[pointer_line][pointer_char]

def Compare_char(add_char): # Ελεγχος αν ειναι '<' ή Ελληνικος χαρακτήρας
	global mode
	global file
	global pointer_char
	global pointer_line

	# if add_char == '/' and file[pointer_line][pointer_char + 1] == '/' and mode == 3:
	# 	GetChar_next()
	if add_char == '<':
		Define_mode()

	if add_char == '?':
		End_php_tag()

	if add_char == '>':
		End_html_mode()
	
	for gr in GR_LIST:
		if add_char == gr:
			greek_mode()

def Define_mode(): # Ελεγχει το '<' αν ειναι tag της html ή αν ειναι php (mode =)
	global pointer_char
	global pointer_line
	global file
	global mode
	temp_string = ''
	pointer_restore = pointer_char
	line_restore = pointer_line

	
	if file[pointer_line][pointer_char] == '<': # Φτιαξε το temp_string για να δουμε τη εχει μετα το συμβολο <
		for x in range(1,15):
			temp_string = temp_string + file[pointer_line][pointer_char]
			GetChar_next();
			if file[pointer_line][pointer_char].isspace() or file[pointer_line][pointer_char] == '>':
				temp_string = temp_string + file[pointer_line][pointer_char]
				break
			

	if '<?php' == temp_string.strip(): # Αν temp_sting ειναι PHP
		mode = 3 # PHP mode
		pointer_char = pointer_restore + 2
		pointer_line = line_restore
		return

	if '<?=' in temp_string.strip(): # Αν temp_sting ειναι PHP
		mode = 3 # PHP mode
		pointer_char = pointer_restore + 2
		pointer_line = line_restore
		return

	if '<?xml' == temp_string.strip():
		mode = 4 # XML mode
		pointer_char = pointer_restore + 2
		pointer_line = line_restore
		return

	for html in HTML_S_LIST:
		text1 = html + '>'
		text2 = html + ' '

		if text1 == temp_string:
			if mode == 3 or mode == 23 or mode == 13:
				mode = 13 # HTML outside Μεσα σε PHP 
				return
			else:
				mode = 1 # HTML outside
				return
		if text2 == temp_string:
			if mode == 3  or mode == 23 or mode == 13:
				mode = 23 # HTML inside Μεσα σε PHP
				pointer_mode = [pointer_restore, line_restore]
				return
			else:
				mode = 2 # HTML inside
				pointer_mode = [pointer_restore, line_restore]
				return
	
	if temp_string == '<script ' or temp_string == '<script>':
		check = 0
		while check != 1:
			check = Find_Script() # SKIP <script> tag
		return

	if temp_string.find('<!--') != -1:
		check = 0
		while check != 1:
			check = Find_Comments() # SKIP <!-- tag
		return
		

	pointer_char = pointer_restore
	pointer_line = line_restore
	return

def End_php_tag(): # Ορίζει το τέλος της PHP ωστε να γυρισει το mode σε 0 
	global pointer_char
	global pointer_line
	global file
	global mode
	temp_string = ''
	pointer_restore = pointer_char
	line_restore = pointer_line

	if mode != 3 and mode != 4:
		return

	if file[pointer_line][pointer_char] == '?':
		for x in range(1,5):
			temp_string = temp_string + file[pointer_line][pointer_char]
			GetChar_next();
			if file[pointer_line][pointer_char].isspace() or file[pointer_line][pointer_char] == '>':
				temp_string = temp_string + file[pointer_line][pointer_char]
				break
	if '?>' == temp_string and mode == 4:
		mode = 3
		return

	if '?>' == temp_string:
		mode = 0
		return
	pointer_char = pointer_restore
	pointer_line = line_restore	

def End_html_mode(): # Αλλάζει το mode οταν κλείνει tag της html
	global pointer_char
	global pointer_line
	global file
	global mode
	temp_string = ''
	pointer_restore = pointer_char
	line_restore = pointer_line

	if mode == 2:
		mode = 1

def Find_Comments(): # SKIP comment <!--
	global pointer_char
	global pointer_line
	global file
	temp_string_1 = ''
 
	while file[pointer_line][pointer_char] != '-':
		GetChar_next()

	if file[pointer_line][pointer_char] == '-':
		for x in range(1,10):
			temp_string_1 = temp_string_1 + file[pointer_line][pointer_char]
			GetChar_next();
			if file[pointer_line][pointer_char].isspace() or file[pointer_line][pointer_char] == '>':
				temp_string_1 = temp_string_1 + file[pointer_line][pointer_char]
				break
		if temp_string_1.find('-->') != -1:
			return 1

def Find_Script(): # SKIP <script>
	global pointer_char
	global pointer_line
	global file
	temp_string_1 = ''
 
	while file[pointer_line][pointer_char] != '<':
		GetChar_next()

	if file[pointer_line][pointer_char] == '<':
		for x in range(1,10):
			temp_string_1 = temp_string_1 + file[pointer_line][pointer_char]
			GetChar_next();
			if file[pointer_line][pointer_char].isspace() or file[pointer_line][pointer_char] == '>':
				temp_string_1 = temp_string_1 + file[pointer_line][pointer_char]
				break

		if temp_string_1 == '</script>' or temp_string_1 == '</script':
			return 1

def greek_mode(): # Εξαγωγή Ελλήνικής φράσης
	global pointer_char
	global pointer_line
	global mode
	global file
	global export_string
	global pointer_mode


	if mode == 1: #HTML outside tag
		line_restore = pointer_line
		pointer_restore = pointer_char
		while file[pointer_line][pointer_char] != '<':
			export_string = export_string + file[pointer_line][pointer_char]
			GetChar_next()
		Export_Array(export_string, import_file, line_restore, pointer_restore)
		line_restore = 0
		pointer_restore = 0
		
		if file[pointer_line][pointer_char] == '<':
			pointer_char = pointer_char - 1
		export_string = ''
	else: #REST php html etc...
		line_restore = pointer_line
		pointer_restore = pointer_char
		while file[pointer_line][pointer_char] in GR_LIST or file[pointer_line][pointer_char] == ' ':
			export_string = export_string + file[pointer_line][pointer_char]
			GetChar_next()
		Export_Array(export_string, import_file, line_restore, pointer_restore)
		export_string = ''
		line_restore = 0
		pointer_restore = 0

	#	if mode == 2: #HTML inside tag
	#
	#		while file[pointer_line][pointer_char] != '\'' or file[pointer_line][pointer_char] != '\"':
	#				export_string = export_string + file[pointer_line][pointer_char]
	#				GetChar_next()
	#
	#		if file[pointer_line][pointer_char] == temp_pointer:
	#			pointer_char = pointer_char - 1
	#			Export_Array(export_string, import_file, pointer_line, pointer_char)
	#		export_string = ''
	#
	#
	#	if mode == 3: #PHP
	#
	#		Export_Array(file[pointer_line][pointer_char], import_file, pointer_line, pointer_char)
	
	
	#	if mode == 13: #PHP
	#		Export_Array(file[pointer_line][pointer_char], import_file, pointer_line, pointer_char)
	#
	#
	#	if mode == 23: #PHP
	#		Export_Array(file[pointer_line][pointer_char], import_file, pointer_line, pointer_char)

Export_Array_counter = 0
def Export_Array(string, filename, line, column): # Εξαγωγή πίνακα για την δημιουργία "define file"
	global mode
	global check_table
	global Export_Array_counter
	clear_string = string.rstrip()
	line = line + 1
	column = column + 1

	#EXPORT TO ARRAY

	
	new_position = [filename,line,column,mode,Export_Array_counter]
	Export_Array_counter = Export_Array_counter + 1
	new_entry = {
		'key': clear_string,
		'position': [new_position],
		}

	c=-1
	for dic in export_array:
		c = c+1
		if dic['key'] == clear_string:
			break



	if clear_string in check_table:
		export_array[c]['position'].append(new_position)
	else:
		check_table.append(clear_string)
		export_array.append(new_entry)

	
	# if clear_string in export_array:
	# 	export_array['Position'].append(new_position)
	# else:
	# 	export_array['key'] = entry

def Export_php_define(): #EXPORT TO FILE για strings ενδιάμεσα σε tag της html <html>ΚΕΙΜΕΝΟ</html>
	php_Var_Array = []
	for key in export_array:
		for pos in key['position']:
			if pos[3] == 1:
				clear_string_for_php = key['key'].replace('"','\\"')
				clear_greeklish = Convert_To_Greeklish(key['key'])

				while clear_greeklish in php_Var_Array:
					clear_greeklish = clear_greeklish + '_C'
				php_Var_Array.append(clear_greeklish)
				clear_string_for_php = clear_string_for_php.replace('\n','').replace('\r','')
				E = open("export_var.txt", "a", encoding='utf8')
				new_entry = 'define("'+ clear_greeklish + '", ' + '"' + clear_string_for_php + '")' + '\n'
				E.write(new_entry)
				E.close()
				break

def Export_NOT_php_define(): #ΞΑΝΑ ΔΕΣ ΤΟ !!!!!!!!!! #EXPORT TO FILE Όλα τα string εκτος απο αυτα που είναι ενδιάμεσα απο tag της html
	php_Var_Array = []
	for key in export_array:
		for pos in key['position']:
			if pos[3] != 1:
				clear_string_for_php = key['key'].replace('"','\\"')
				clear_greeklish = Convert_To_Greeklish(key['key'])

				while clear_greeklish in php_Var_Array:
					clear_greeklish = clear_greeklish + '_C'
				test_array.append(clear_greeklish)

				E = open("export_NOT_var.txt", "a", encoding='utf8')
				new_entry = 'define("'+ clear_greeklish + '", ' + '"' + clear_string_for_php + '")' + '\n'
				E.write(new_entry)
				E.close()
				break

def Convert_To_Greeklish(string):
	new_string = string
	new_string = new_string.replace('ς', 's')
	new_string = new_string.replace('ε', 'e')
	new_string = new_string.replace('ρ', 'r')
	new_string = new_string.replace('τ', 't')
	new_string = new_string.replace('υ', 'u')
	new_string = new_string.replace('θ', 'th')
	new_string = new_string.replace('ι', 'i')
	new_string = new_string.replace('ο', 'o')
	new_string = new_string.replace('π', 'p')
	new_string = new_string.replace('α', 'a')
	new_string = new_string.replace('σ', 's')
	new_string = new_string.replace('δ', 'd')
	new_string = new_string.replace('φ', 'f')
	new_string = new_string.replace('γ', 'g')
	new_string = new_string.replace('η', 'i')
	new_string = new_string.replace('ξ', 'ks')
	new_string = new_string.replace('κ', 'k')
	new_string = new_string.replace('λ', 'l')
	new_string = new_string.replace('ζ', 'z')
	new_string = new_string.replace('χ', 'ch')
	new_string = new_string.replace('ψ', 'ps')
	new_string = new_string.replace('ω', 'o')
	new_string = new_string.replace('β', 'v')
	new_string = new_string.replace('ν', 'n')
	new_string = new_string.replace('μ', 'm')
	new_string = new_string.replace('ς', 's')
	new_string = new_string.replace('Ε', 'E')
	new_string = new_string.replace('Ρ', 'R')
	new_string = new_string.replace('Τ', 'T')
	new_string = new_string.replace('Υ', 'Y')
	new_string = new_string.replace('Θ', 'TH')
	new_string = new_string.replace('Ι', 'I')
	new_string = new_string.replace('Ο', 'O')
	new_string = new_string.replace('Π', 'P')
	new_string = new_string.replace('Α', 'A')
	new_string = new_string.replace('Σ', 'S')
	new_string = new_string.replace('Δ', 'D')
	new_string = new_string.replace('Φ', 'F')
	new_string = new_string.replace('Γ', 'G')
	new_string = new_string.replace('Η', 'I')
	new_string = new_string.replace('Ξ', 'KS')
	new_string = new_string.replace('Κ', 'K')
	new_string = new_string.replace('Λ', 'L')
	new_string = new_string.replace('Ζ', 'Z')
	new_string = new_string.replace('Χ', 'CH')
	new_string = new_string.replace('Ψ', 'PS')
	new_string = new_string.replace('Ω', 'O')
	new_string = new_string.replace('Β', 'B')
	new_string = new_string.replace('Ν', 'N')
	new_string = new_string.replace('Μ', 'M')
	new_string = new_string.replace('Ά', 'A')
	new_string = new_string.replace('Έ', 'E')
	new_string = new_string.replace('Ύ', 'Y')
	new_string = new_string.replace('Ί', 'I')
	new_string = new_string.replace('Ό', 'O')
	new_string = new_string.replace('Ή', 'I')
	new_string = new_string.replace('Ώ', 'O')
	new_string = new_string.replace('Ϊ', 'I')
	new_string = new_string.replace('Ϋ', 'Y')
	new_string = new_string.replace('έ', 'E')
	new_string = new_string.replace('ύ', 'Y')
	new_string = new_string.replace('ί', 'I')
	new_string = new_string.replace('ό', 'O')
	new_string = new_string.replace('ά', 'A')
	new_string = new_string.replace('ή', 'I')
	new_string = new_string.replace('ώ', 'O')
	new_string = new_string.replace('ϊ', 'I')
	new_string = new_string.replace('ϋ', 'Y')
	new_string = new_string.replace('  ', '')
	new_string = new_string.replace(' ', '_')

	for x in new_string:
		if not x.isalnum():
			if x == '_':
				pass
			else:
				new_string = new_string.replace(x, '')
	new_string = 'VAR_' + new_string + '_END'
	new_string = new_string.upper()
	return new_string

def Read_Path(path): # Διαβάζει όλα τα αρχεία απο της μεταβλητης path και δημηουργή το EXPORT_ARRAY 
	global pointer_line
	global pointer_char
	global mode
	global export_string
	global pointer_mode
	global file
	global import_file

	clear_entry = []
	entries = []

	for root, dirs, files in os.walk(path, topdown=False):
		for files_1 in files:
			mix = root.replace('\\','/') + '/' + files_1
			entries.append(mix)

	for entry in entries:
		if entry.endswith('.php'):
			clear_entry.append(entry)
	

	for import_file in clear_entry:
	
		print(import_file)
	
		with open(import_file, encoding='utf8') as f:
			file = f.readlines()
		if len(file) == 0:
			continue
	
		pointer_line = 0
		pointer_char = -1
		mode = 0 #0 None -  1 HTML OUTSIDE - 2 HTML INSIDE - 3 PHP
		export_string = ''
		pointer_mode = [0,0]
	
		while GetChar_next() != None :
			Compare_char(file[pointer_line][pointer_char]) #Read files from path

def Export_Array_sorted(): # Εξαγωγή πίνακα κατάλληλο για χρήση αντικατάστασεις στα τελικα αρχεία
	global export_array
	sorted_array = []
	new_path = ''
	entries = []
	clear_entry = []
	for root, dirs, files in os.walk(path, topdown=False):
		for files_1 in files:
			mix = root.replace('\\','/') + '/' + files_1
			entries.append(mix)

	for entry in entries:
		if entry.endswith('.php'):
			clear_entry.append(entry)	
	print(clear_entry)

	for clear_path in clear_entry:
		new_entry = []
		for key in export_array:
			item = []
			
			for x in key['position']:

				if x[0] == clear_path and x[3] == 1:
					item = [key['key'],x[1],x[2],x[4]]
					new_entry.append(item)
					new_path = x[0]
					from operator import itemgetter
					new_entry = sorted(new_entry, key=itemgetter(3) , reverse = True)

		if new_path != '' and new_entry != []:
			new_item = {
				'path': new_path,
				'item': new_entry
			}
			sorted_array.append(new_item)

	return sorted_array

def Replace_vars(): # Υπο κατασκευή
	array = Export_Array_sorted()

	#with open('export_var.txt', 'r', encoding='utf8') as f:
	#	ex_file = f.readlines()

	for direction in array:
		print('OPEN PATH => ' + direction['path'])
		with open(direction['path'], 'r', encoding='utf8') as f:
			lines = f.readlines()
		with open('export_var.txt', 'r', encoding='utf8' ) as e:
			e_lines = e.readlines()

		for items in direction['item']:
			items[0]#string
			items[1]#line
			items[2]#column
			items[3]#order


			pattern = ''
			for c in e_lines:
				c = c.replace('\\','')
				c1 = c
				t = re.findall('define\("VAR_.*", "',c1)
				c1 = c1.replace(t[0] , '')
				c1 = c1[:-3]
				items_clear = items[0].replace('\\','')
				if items_clear == c1:

					t = re.findall('", ".*"\)',c)
					t2 = re.findall('define\("',c)
					pattern = c.replace(t[0] , '')
					pattern = pattern.replace(t2[0] , '')
					break
			pattern = pattern.lstrip()
			pattern = pattern.rstrip()
			replace_word = '<?=' + pattern + '?>'
			lines[items[1] - 1] = lines[items[1] - 1][:items[2]-1] + replace_word + lines[items[1] - 1][(items[2]-1) + len(items_clear):]

		with open(direction['path'], 'w', encoding='utf8') as f:
			f.writelines(lines)


############## MAIN PROGRAM ##################

path = 'C:/xampp/htdocs/I-Home translate/Live'

Read_Path(path)
Export_php_define()
print(Export_Array_sorted())
Replace_vars()


