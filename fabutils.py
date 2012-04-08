from fabric.api import local, settings, require, run, sudo, env, cd, hide
from fabric.contrib.files import exists, append
import os

# util functions
def ensure_link(target, source):
	if exists(target):
		run('rm -rf ' +  target)
	run('ln -s %s %s' % (source, target))

def ensure_dir(directory):
	if not exists(directory):
		run('mkdir -p ' + directory)

def program_exists(name):
	with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
		result = run('which ' + name)
	return False if result.return_code else True

def osname():
	if not env.get('osname'):
		with hide('running', 'stdout'):
			env.osname = run('uname')
	return env.osname

def is_macos():
	return osname() == 'Darwin'

def is_linux():
	return osname() == 'Linux'

def ensure_homebrew():
	if not program_exists('brew'):
		run('/usr/bin/ruby -e "$(/usr/bin/curl -fksSL https://raw.github.com/mxcl/homebrew/master/Library/Contributions/install_homebrew.rb)"')

def ensure_git_repo(path, url, pushurl=None, submodules=False):
	if not exists(path):
		ensure_package('git')
		run('git clone %s %s' % (url, path))
		if pushurl:
			with(cd(path)):
				run('git config remote.origin.pushurl %s' % pushurl)
		if submodules:
			with(cd(path)):
				run('git submodule init')
				run('git submodule update')

def find_package_management_program():
	if env.get('install_package_command'):
		return
	if is_linux():
		if program_exists('apt-get'):
			env.install_package_command = 'sudo apt-get install -y'
		elif program_exists('yum'):
			env.install_package_command = 'sudo yum -y install'
	elif is_macos():
		ensure_homebrew()
		env.install_package_command = 'brew'

def ensure_package(name):
	find_package_management_program()
	run('%s %s' % (env.install_package_command, name))

def ensure_python_pkg(name):
	if not program_exists('pip'):
		sudo('easy_install pip')
	sudo('pip install %s' % name)

def ensure_file(name, **kwargs):
	'''
		Optional arguments:
		append: append lines to the end of the file if they're not already existed.
	'''
	if not exists(name):
		run('touch %s' % name)
	if kwargs.get('append'):
		lines = kwargs.get('append')	
		if not isinstance(lines, list):
			lines = lines.split('\n')
		append(name, lines)

