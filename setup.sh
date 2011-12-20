#!/bin/bash
git submodule init
git submodule update
export cfg_dir=`pwd`

# update vim-setup
cd .vim
git checkout master
git submodule init
git submodule update

# setup symbolic links

cd ~
ln -sf $cfg_dir/.vim
ln -sf $cfg_dir/.vim/.vimrc_common
ln -sf $cfg_dir/.zshrc_common
ln -sf $cfg_dir/.ctags
ln -sf $cfg_dir/.screenrc
ln -sf $cfg_dir/.terminfo

echo 'source ~/.zshrc_common' > ~/.zshrc
echo 'source ~/.vimrc_common' > ~/.vimrc

echo 'setopt ALL_EXPORT' > ~/.zshenv
echo 'path=( . $path )' >> ~/.zshenv
