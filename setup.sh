#/bin/sh

set $cfg_dir = `pwd`

cd ~
ln -s $cfg_dir/.vim/.vimrc_common
ln -s $cfg_dir/.zshrc_common
ln -s $cfg_dir/.ctags
ln -s $cfg_dir/.screenrc
ln -s $cfg_dir/.terminfo

echo 'source ~/.zshrc_common' > ~/.zshrc
echo 'source ~/.vimrc_common' > ~/.vimrc

echo 'setopt ALL_EXPORT' > ~/.zshenv
echo 'path=( . $path )' >> ~/.zshenv
