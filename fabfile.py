from fabric.api import local, exist, contains, settings, require, run, sudo
import os

# util functions
def ensure_link(target, source):
	if exists(target):
		run('rm -rf target')
	run('ln -s %s %s' % (source, target))

def ensure_dir(directory):
	if not exists(directory):
		run('mkdir -p ' + directory)

def program_exists(name):
	with settings(warn_only=True):
		result = run('which ' + name)
	return False if result.return_code else True

def osname():
	if not env.get('osname')
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
		run('git clone %s %s' % (path, url))
		if pushurl:
			with(cd(path)):
				run('git config remote.origin.pushurl %s' % pushurl)
		if submodules:
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
		env.install_package_command = find_program('brew')

def ensure_package(name):
	require('install_package_command', provided_by=find_package_management_program)
	run('%s %s' % (env.install_package_command, name))

def ensure_file(name, append=None):
	if not exists(name):
		run('touch %s' % name)
	if append:
		if not isinstance(append, list):
			append = append.split('\n')
		append(name, append)

# public apis
def ssh_localhost():
	home_dir = os.getenv('HOME')
	local('mkdir -p ~/.ssh')
	if not os.path.exists(home_dir + '/.ssh/id_rsa'):
		local("ssh-keygen -t rsa -N'' ~/.ssh/id_rsa")
	local('ssh-keygen -y -f ~/.ssh/id_rsa >> ~/.ssh/authorized_keys')

def install_vim73():
	if not exists('/tmp/vim73'):
		ensure_package('wget')
		with(cd('/tmp')):
			run('wget -q -O - ftp://ftp.vim.org/pub/vim/unix/vim-7.3.tar.bz2 | tar jx')
	with(cd('/tmp/vim73')):
		run('./configure --enable-pythoninterp --enable-rubyinterp --enable-perlinterp --enable-cscope')
		run('make')
		sudo('make install')

def dotrepo():
	ensure_git_repo('~/configs', 'git://github.com/yejianye/tools-config.git', pushurl='git@github.com:yejianye/tools-config.git')

def vim():
	# get vim version
	ensure_git_repo('~/.vim', 'git://github.com/yejianye/vim-setup.git', pushurl='git@github.com:yejianye/vim-setup.git', submodules=True)
	ensure_link('~/.vimrc_common', '~/.vim/.vimrc_common')
	ensure_file('~/.vimrc', append='source ~/.vimrc_common')
	# With Mac gcc and make should be installed with Xcode
	if not is_macos():
		ensure_package('gcc')
		ensure_package('make')
	with(cd('~/.vim/bundle/vimproc'))
		run('make -f make_gcc.mak')
	# setup pushurl for submodules
	with(cd('~/.vim/bundle/snipMate')):
		run('git config remote.origin.pushurl git@github.com:yejianye/snipmate.vim.git')
	with(cd('~/.vim/bundle/textobj_function')):	
		run('git config remote.origin.pushurl git@github.com:yejianye/vim-textobj-function.git')
	with(cd('~/.vim/vim-ref-jquery')):
		run('git config remote.origin.pushurl git@github.com:yejianye/vim-ref-jquery.git')
	with(cd('~/.vim/jshint')):
		run('git config remote.origin.pushurl git@github.com:yejianye/jshint.vim.git')

def zsh():
	ensure_package('zsh')
	ensure_link('~/.zshrc_common', '~/configs/.zshrc_common')
	ensure_file('~/.zshrc', append='source ~/.zshrc_common')
	ensure_file('~/.zshenv', append=['setopt ALL_EXPORT', 'path=( . ~/bin ~/localbin $path)'])
	ensure_git_repo('~/bin', 'git://github.com/yejianye/util-scripts.git', pushurl='git@github.com:yejianye/util-scripts.git')
	ensure_dir('~/localbin')

def screen():
	ensure_package('screen')
	ensure_link('~/.screenrc', '~/configs/.screenrc')

def ctags():
	ensure_package('ctags')
	ensure_link('~/.ctags', '~/configs/.ctags')

def terminfo():
	ensure_link('~/.terminfo', '~/configs/.terminfo')

def all():
	dotrepo()
	zsh()
	screen()
	ctags()
	terminfo()
	vim()
