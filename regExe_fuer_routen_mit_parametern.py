import re

# RegExe um Routen mit Parametern nutzen zu können.
# Könnte den aktuellen 1:1-Match in Kernel ersetzen.

pIn = '/api/get/42/do/jubel'
path = '/api/get/{id}/do/{what}'
params = {
	'id': 'int',
	'what': 'str'
}


for placeHolder in re.findall(r'\{[\w]{1,}\}', path):
	print(placeHolder)
	placeHolderPlain = placeHolder.strip('{}')
	if 'str' == params[placeHolderPlain]:
		to = "(?P<{n}>\\w{{1,}})".format(n=placeHolderPlain)
	elif 'int' == params[placeHolderPlain]:
		to = "(?P<{n}>[0-9]{{1,}})".format(n=placeHolderPlain)
	else:
		print('Not allowed Type: ' . params[placeHolderPlain])
		continue

	path = path.replace(placeHolder, to)

print(path)
print('-------------------')


matches = re.search(path, pIn)

p = {}
for placeHolder in params:
	print(matches.group(placeHolder))
	if 'str' == params[placeHolder]:
		p[placeHolder] = matches.group(placeHolder)
	elif 'int' == params[placeHolder]:
		p[placeHolder] = int(matches.group(placeHolder))

print(p)

