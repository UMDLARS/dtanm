#!/bin/bash

#TODO: Allow ssh access for team users.
#arg1 is the number of teams

[ ! -d "pack" ] && echo "You must install a pack first!!!" && exit 1

ROOT="/"
CCTF_PATH=$ROOT"var/cctf"
CCTF_HOME=$ROOT"var/cctf"
HOME_PATH=$ROOT"home"
WWW_PATH=$ROOT"var/www/html"
SRC_NAME="$(cat pack/info/src_name)"
BIN_NAME="$(cat pack/info/bin_name)"
PACK_NAME="$(cat pack/info/pack_name)"
# GIT_REPO="/home/ubuntu/workspace/cctf"

echo "Your root is '$ROOT'"
echo "You have requested $1 teams."
echo "You are running this as $USER."
echo "You are installing the '$PACK_NAME'"

if [[ -z "${BIN_NAME// }" ]]; then
  # There is not bin name therefore it must be a script program
  readable_bin=true
else 
  # It makes a binary that can be run.
  readable_bin=false
fi

# check if 1st arg is a number
re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
   echo "Error: 1st arg must be the number of teams." >&2; exit 1
fi

# check if number of teams is positive
if [ $1 -le 0 ]
  then
    echo "Error: number of teams must be positive." >&2; exit 1
fi

echo "Are you sure that you would like to continue (y or n)? Make sure you have backed up any data that you would to see again before continuing."
read response
until [[ $response == "y" || $response == "n" ]] ; do
    echo "You must enter y or n!"
    read response
done
if [ $response == "n" ] ; then
    echo "Exiting without error."
    exit 0
fi

echo "Removing old team users and directories..."
pushd /home
for t in team*
do 
	echo $t
	sudo userdel -r $t
done
popd

echo "Getting latest code..."
#TODO: make sure that the repo is clean and maybe look for the latest release tag or something
# git pull
# dir=`mktemp -d` && cd $dir
# git clone "$GIT_REPO" code
# cd code
echo "Copying pack/docs/www to $WWW_PATH ..."
sudo cp -r pack/docs/www/* $WWW_PATH

echo "Recreating dist directory..."
[ -d "dist" ] && sudo rm -rf "dist"

echo "Copying bin/* to dist/bin/* ..."
mkdir dist
mkdir dist/bin
mkdir dist/src
cp -r bin dist

echo "Copying pack/src/* to dist/src/* ..."
cp -r pack/src dist
echo "Copying pack/env/* to dist/env/* ..."
cp -r pack/env dist

#NOTE: Maybe this should be in the Makefile and then just call make.
echo "Compiling gold..."
#gcc -Wall -O -std=gnu99 -o bin/gold src/gold.c
cd pack/gold
make
cd ../..
echo "Copying gold to dist..."
cp pack/gold/gold dist/bin/prog
chmod 770 dist/bin/prog

echo "Cleaning..."
echo "Removing team home directories if any exist..."
if ls $HOME_PATH/team* 1> /dev/null 2>&1; then
    sudo rm -rf $HOME_PATH/team*
fi
echo "Removing $CCTF_PATH if it exists..."
[ -d "$CCTF_PATH" ] && sudo rm -rf "$CCTF_PATH"
sudo mkdir -p $CCTF_PATH

echo "Starting to place new files..."

echo "Creating cctf user if not already created..."
#echo "Hey CCFT_HOME='$CCTF_HOME' '$CCTF_PATH'"
id -u cctf &>/dev/null || sudo useradd cctf
[ ! -d "$CCTF_HOME" ] && sudo mkdir -p $CCTF_HOME
sudo chown -hR cctf:cctf $CCTF_HOME
#sudo usermod -d $HOME_PATH/cctf cctf
echo "Setting cctf's home to $CCTF_HOME ..."
sudo usermod -d $CCTF_HOME cctf
#TODO: make this replace the line that sets the teams var if it exists already
echo "Setting TEAMS var in cctf..."
#sudo echo "export TEAMS=$1" >> $HOME_PATH/cctf/.bashrc
#echo "export TEAMS=$1" | sudo tee -a $CCFT_HOME/.bashrc
echo "export TEAMS=$1" | sudo tee -a $CCTF_HOME/.bashrc
echo "export HOME_PATH=\"$HOME_PATH\"" | sudo tee -a $CCTF_HOME/.bashrc
echo "export CCTF_PATH=\"$CCTF_PATH\"" | sudo tee -a $CCTF_HOME/.bashrc
echo "export PATH=\"$CCTF_PATH/bin:\$PATH\"" | sudo tee -a $CCTF_HOME/.bashrc
echo "export SRC_NAME=\"$SRC_NAME\"" | sudo tee -a $CCTF_HOME/.bashrc
echo "export BIN_NAME=\"$BIN_NAME\"" | sudo tee -a $CCTF_HOME/.bashrc
sudo chown -h cctf:cctf $CCTF_HOME/.bashrc
sudo touch $CCTF_PATH/attacklist.txt
sudo touch $CCTF_PATH/scoreboard.txt

echo "Copying in src files..."
sudo cp -r dist/src $CCTF_PATH/src

echo "Copying in env files..."
sudo cp -r dist/env $CCTF_PATH/env
echo "Making read only..."
#TODO: make this work even with sub directories. Dirs: 555 and files: 444
sudo chmod -R 444 $CCTF_PATH/env
sudo chmod 755 $CCTF_PATH/env

echo "Copying in bin files..."
sudo cp -r dist/bin $CCTF_PATH/bin
#TODO: make least privilege the default! aka 700
sudo chmod 755 $CCTF_PATH/bin/*
echo "Copying in tips..."
sudo cp pack/docs/tips $CCTF_PATH/bin/tips
echo "Fixing permissions..."
sudo chmod 700 $CCTF_PATH/bin/testprog.py
sudo chmod 700 $CCTF_PATH/bin/scorebot.py
sudo chmod 700 $CCTF_PATH/bin/manager.py

# this is setting all the files currently in cctf (this includes all except dirs)
sudo chown -hR cctf:cctf $CCTF_PATH
sudo chmod u+s $CCTF_PATH/bin/gold

echo "Creating dir directories..."
sudo mkdir $CCTF_PATH/dirs
sudo chown -h cctf:cctf $CCTF_PATH/dirs
# for each team
for i in `seq 1 $1`;
do
    sudo usermod -G team$i -a cctf
    sudo mkdir $CCTF_PATH/dirs/team$i
    sudo mkdir $CCTF_PATH/dirs/team$i/attacks
    sudo mkdir $CCTF_PATH/dirs/team$i/bin
    sudo mkdir $CCTF_PATH/dirs/team$i/src

    sudo chown -hR cctf:team$i $CCTF_PATH/dirs/team$i
    sudo chmod 770 $CCTF_PATH/dirs/team$i/attacks
    sudo chmod 770 $CCTF_PATH/dirs/team$i/src
    if [ "$readable_bin" = true ]; then
      sudo chmod 770 $CCTF_PATH/dirs/team$i/bin
    else
      sudo chmod 775 $CCTF_PATH/dirs/team$i/bin
    fi
done


echo "Creating team home directories"
for i in `seq 1 $1`;
do
    # create team user
    id -u team$i &>/dev/null || sudo useradd team$i

    # Remove home dir if exists
    [ -d "$HOME_PATH/team$i" ] && sudo rm -rf $HOME_PATH/team$i
    # create team home
    sudo mkdir -p $HOME_PATH/team$i
    # set home directory
    sudo usermod -d $HOME_PATH/team$i team$i
    # set default shell to bash
    sudo chsh -s /bin/bash team$i

    sudo cp -R "dist/src/." "$HOME_PATH/team$i"
    sudo cp "$HOME_PATH/team$i/$SRC_NAME" "$HOME_PATH/team$i/$SRC_NAME.orig"
    if [ "$readable_bin" = true ]; then
      sudo chmod -R 740 $HOME_PATH/team$i/*
    else
      sudo chmod -R 640 $HOME_PATH/team$i/*
    fi
    sudo chmod 440 $HOME_PATH/team$i/$SRC_NAME.orig
    sudo ln -s $CCTF_PATH/dirs/team$i/attacks $HOME_PATH/team$i/attacks

    cd dist/env
    for f in *
    do
      sudo cp "$f" "$HOME_PATH/team$i/$f"
      sudo chmod 444 "$HOME_PATH/team$i/$f"
    done
    cd ../..
    #sudo chmod 444 "dist/env/."
    #sudo cp -Rp "dist/env/." "$HOME_PATH/team$i"

    #sudo cp dist/src/Makefile $HOME_PATH/team$i/Makefile
    #sudo chmod 640 $HOME_PATH/team$i/Makefile

    echo "Setting TEAMS var in team$i..."
    echo "export TEAMS=$1" | sudo tee -a $HOME_PATH/team$i/.bash_login
    echo "export PATH=\"$CCTF_PATH/bin:\$PATH\"" | sudo tee -a $HOME_PATH/team$i/.bash_login
    echo "export CCTF_PATH=\"$CCTF_PATH\"" | sudo tee -a $HOME_PATH/team$i/.bash_login
    echo "export SRC_NAME=\"$SRC_NAME\"" | sudo tee -a $HOME_PATH/team$i/.bash_login
    echo "export BIN_NAME=\"$BIN_NAME\"" | sudo tee -a $HOME_PATH/team$i/.bash_login
    sudo chown -h team$i:team$i $HOME_PATH/team$i/.bash_login

    # change the group and owner to the team user.
    sudo chown -hR team$i:team$i $HOME_PATH/team$i
done


echo "Would you like to reset the team users passwords (y or n)?"
read response
until [[ $response == "y" || $response == "n" ]] ; do
    echo "You must enter y or n!"
    read response
done
echo "The following are the passwords for the teams."
if [ $response == "y" ] ; then
    for i in `seq 1 $1`;
    do
        #TODO: remove the last char from the base64 convertion. (It is always an =)
        NEWPASS=`head -c 8 /dev/urandom | base64`
        echo "Team #$i: $NEWPASS"
        echo "team$i:$NEWPASS" | sudo chpasswd
    done
fi

export TEAMS="$1"

# set environment varibles
echo ""
echo "Done."
echo "All bots should be run as the cctf user!"
# echo ""
# echo "Make sure that you add the following lines to your '.bashrc'"
# echo "export TEAMS=$1"
