from setuptools import setup
version = '0.1.4'
setup(
	name = 'tradersbot',
	packages = ['tradersbot'], # this must be the same as the name above
	version = version,
	description = 'Python wrapper for mangocore API',
	author = 'Traders@MIT',
	author_email = 'traders@mit.edu',
	license = 'LICENSE.txt',
	url = 'https://github.com/traders/mangocore-client',
	download_url = 'https://github.com/traders/mangocore-client/tarball/' + version,
	install_requires = ['tornado'],
	keywords = ['MIT', 'quant', 'traders', 'trading'],
	classifiers = [],
)
