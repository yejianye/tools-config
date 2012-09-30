from fabric.api import env, local, settings, run, sudo, cd, task
from fabric.contrib.files import exists, upload_template, sed
import sys, os
try:
	from fabtask.files import ensure_link, ensure_file, ensure_dir, ensure_bin_path
	from fabtask.utils import is_macos, is_linux
	from fabtask.packages import ensure_package, ensure_python_pkg
	from fabtask.vcs import ensure_git_repo
except ImportError:
	print "Fabtask package not found. Please run 'fab fabtask' to install it"

env.use_ssh_config = True

@task
def fabtask(source=False, path='.'):
	with settings(warn_only=True):
		pip = local('which pip', capture=True)
	if not pip.succeeded:
		local('sudo easy_install pip')
	with settings(warn_only=True):
		git = local('which git', capture=True)
	if not git.succeeded:
		local('sudo apt-get install git')
	if source:
		with cd(path):
			local('git clone git://github.com/yejianye/fabtask.git')
	else:
		local('sudo pip install git+git://github.com/yejianye/fabtask.git')

@task
def ssh_localhost():
	home_dir = os.getenv('HOME')
	local('mkdir -p ~/.ssh')
	if not os.path.exists(home_dir + '/.ssh/id_rsa'):
		local("ssh-keygen -t rsa -N'' ~/.ssh/id_rsa")
	local('ssh-keygen -y -f ~/.ssh/id_rsa >> ~/.ssh/authorized_keys')

@task
def install_vim73():
	ensure_package('gcc')
	ensure_package('libncurses5-dev')
	if not exists('/tmp/vim73'):
		ensure_package('wget')
		with(cd('/tmp')):
			run('wget -q -O - ftp://ftp.vim.org/pub/vim/unix/vim-7.3.tar.bz2 | tar jx')
	with(cd('/tmp/vim73')):
		run('./configure --enable-pythoninterp --enable-rubyinterp --enable-cscope')
		run('make')
		sudo('make install')

@task
def dotrepo():
	ensure_git_repo('configs', 'git://github.com/yejianye/tools-config.git', pushurl='git@github.com:yejianye/tools-config.git')

@task
def vim():
	# get vim version
	ensure_git_repo('.vim', 'git://github.com/yejianye/vim-setup.git', pushurl='git@github.com:yejianye/vim-setup.git', submodules=True)
	ensure_link('.vimrc_common', '~/.vim/.vimrc_common')
	ensure_file('.vimrc', append='source ~/.vimrc_common')
	# With Mac gcc and make should be installed with Xcode
	if not is_macos():
		ensure_package('gcc')
		ensure_package('make')
	with(cd('~/.vim/bundle/vimproc')):
		if is_macos():
			run('make -f make_mac.mak')
		elif is_linux():
			run('make -f make_unix.mak')
	# setup pushurl for submodules
	with(cd('~/.vim/bundle/textobj_function')):	
		run('git config remote.origin.pushurl git@github.com:yejianye/vim-textobj-function.git')
	with(cd('~/.vim/bundle/vim-ref-jquery')):
		run('git config remote.origin.pushurl git@github.com:yejianye/vim-ref-jquery.git')
	with(cd('~/.vim/bundle/jshint')):
		run('git config remote.origin.pushurl git@github.com:yejianye/jshint.vim.git')

@task
def zsh():
	ensure_package('zsh')
	ensure_git_repo('~/.oh-my-zsh', 'git://github.com/yejianye/oh-my-zsh.git', pushurl='git@github.com:yejianye/oh-my-zsh.git')
	ensure_link('.zshrc_common', 'configs/.zshrc_common')
	ensure_file('.zshrc', append='source ~/.zshrc_common')
	ensure_file('.zshenv', append=['setopt ALL_EXPORT'])
	ensure_dir('~/bin')
	ensure_git_repo('~/utils', 'git://github.com/yejianye/util-scripts.git', pushurl='git@github.com:yejianye/util-scripts.git')
	ensure_bin_path(['.', '~/bin', '~/utils'])

@task
def watcher():
	ensure_python_pkg('pyinotify')
	ensure_git_repo('~/watcher', 'git://github.com/splitbrain/Watcher.git')
	ensure_bin_path('~/watcher')
	if not exists('~/.watcher.ini'):
		run('cp ~/watcher/watcher.ini ~/.watcher.ini')

@task
def gitconfig(name='Ryan Ye', email='yejianye@gmail.com'):
	upload_template('gitconfig', '.gitconfig', context={'name': name, 'email' : email})	

@task
def screen():
	ensure_package('screen')
	ensure_link('.screenrc', 'configs/.screenrc')

@task
def tmux():
	ensure_package('tmux')
	ensure_link('.tmux.conf', 'configs/.tmux.conf')
	if is_macos():
		ensure_link('.tmux.platform.conf', 'configs/.tmux.mac.conf')
	else:
		ensure_file('.tmux.platform.conf')

@task
def ctags():
	if is_macos():
		ensure_package('ctags', '--HEAD')  # Ensure to get Ctags trunk for Objective-C support
	else:
		ensure_package('ctags')
	ensure_link('.ctags', 'configs/.ctags')

@task
def terminfo():
	ensure_link('.terminfo', 'configs/.terminfo')

@task
def python():
	pkgs = [
		'ipython', 
		'ipdb',
		'pylint',
		'fabric',
		'requests'
	]
	[ensure_python_pkg(pkg) for pkg in pkgs]

@task
def wordpress_nginx():
	if not is_linux():
		print 'This task is only supported on linux' 
	# install LEMP (nginx + mysql + php)
	pkgs = ['mysql-server', 'mysql-client', 'nginx', 'php5', 'php5-fpm', 'php5-mysql', 'wordpress']
	#[ensure_package(pkg) for pkg in pkgs]
	sed('/etc/php5/fpm/php.ini', '^;? *cgi.fix_pathinfo *= *1', 'cgi.fix_pathinfo=0', use_sudo=True)
	upload_template('wp_blog', '/etc/nginx/sites-available/wp_blog', use_sudo=True,
		context={'server_name' : 'ryanye.me, blog.ryanye.me, www.ryanye.me'})	
	with cd('/etc/nginx/sites-enabled/'):
		sudo('ln -sf ../sites-available/wp_blog')
	sudo('service nginx restart')
	sudo('bash /usr/share/doc/wordpress/examples/setup-mysql -n wordpress blog.ryanye.me')
	# fix uploads directory permission issue
	sudo('chown www-data:www-data -R /srv/www/wp-uploads')
	# set default language to Chinese in wp-config
	print "To allow direct plugin/content upload, add the following line to /etc/wordpress/confg-localhost.php"
	print "    define('FS_METHOD', 'direct');"
	print "To change default language to Chinese,"
	print "    define('WPLANG', 'zh_CN');"

@task
def all():
	dotrepo()
	zsh()
	vim()
	#screen()
	tmux()
	ctags()
	terminfo()
	python()

@task
def test():
	ensure_bin_path(['.', '~/bin', '~/utils', '~/localbin'])
