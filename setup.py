from setuptools import setup
exec(open('tradersbot/version.py').read())
setup(
	name = 'tradersbot',
	packages = ['tradersbot'], # this must be the same as the name above
	version = __version__,
	description = 'Python wrapper for mangocore API',
	author = 'Traders@MIT',
	author_email = 'traders@mit.edu',
	license = 'MIT',
	url = 'https://github.com/traders/mangocore-client',
	download_url = 'https://github.com/traders/mangocore-client/tarball/' + __version__,
	install_requires = ['tornado'],
	keywords = ['MIT', 'quant', 'traders', 'trading'],
	classifiers = [],
)
