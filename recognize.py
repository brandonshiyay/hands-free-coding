import re

'''
integer x is 3'
integer -- int
string -- string
'''
d = {
	'integer':'int',
	'string': 'str'
}


def sign_var(input_str):
	var_type = re.match('^[a-zA-Z]*', input_str).group(0)
	var_name = re.match('%s (.*) is'%var_type, input_str).group(1)
	r = re.compile('(?:is).*$')
	var_val = ' '.join(re.search(r, input_str).group().split(' ')[1:])
	syntax = ''
	print('%s = %s("%s")'%(var_name, d[var_type], var_val))


sign_var('string x is aaa bbb ccc')



s = '''
qowefhowefh ""wfqwf'
'''

print(s)