#!/bin/bash

#TODO: Allow ssh access for team users.
#arg1 is the number of teams

ROOT="/home/ubuntu/workspace/tmp/"
CCTF_PATH=$ROOT"var/cctf"
HOME_PATH=$ROOT"home"
# GIT_REPO="/home/ubuntu/workspace/cctf"

echo "Your root is '$ROOT'"
echo "You have requested $1 teams."
echo "You are running this as $USER."

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

echo "Getting latest code..."
#TODO: make sure that the repo is clean and maybe look for the latest release tag or something
git pull
# dir=`mktemp -d` && cd $dir
# git clone "$GIT_REPO" code
# cd code

#NOTE: Maybe this should be in the Makefile and then just call make.
echo "Compiling gold..."
gcc -Wall -O -std=gnu99 -o bin/gold src/gold.c

echo "Cleaning..."
echo "Removing team home directories if any exist..."
if ls $HOME_PATH/team* 1> /dev/null 2>&1; then
    sudo rm -rf $HOME_PATH/team*
fi
echo "Removing $CCTF_PATH if it exists..."
[ -d "$CCTF_PATH" ] && sudo rm -rf "$CCTF_PATH"

echo "Starting to place new files..."

echo "Creating cctf user if not already created..."
id -u cctf &>/dev/null || sudo useradd cctf
[ ! -d "$HOME_PATH/cctf" ] && sudo mkdir -p $HOME_PATH/cctf
sudo chown -hR cctf:cctf $HOME_PATH/cctf
sudo usermod -d $HOME_PATH/cctf cctf
#TODO: make this replace the line that sets the teams var if it exists already
echo "Setting TEAMS var in cctf..."
#sudo echo "export TEAMS=$1" >> $HOME_PATH/cctf/.bashrc
echo "export TEAMS=$1" | sudo tee -a $HOME_PATH/cctf/.bashrc
echo "export HOME_PATH=\"$HOME_PATH\"" | sudo tee -a $HOME_PATH/cctf/.bashrc
echo "export CCTF_PATH=\"$CCTF_PATH\"" | sudo tee -a $HOME_PATH/cctf/.bashrc
echo "export PATH=\"$CCTF_PATH/bin:\$PATH\"" | sudo tee -a $HOME_PATH/cctf/.bashrc
sudo chown -h cctf:cctf $HOME_PATH/cctf/.bashrc
echo "Creating $CCTF_PATH..."
sudo mkdir -p "$CCTF_PATH"
echo "Building cctf directories..."

sudo touch $CCTF_PATH/attacklist.txt
sudo touch $CCTF_PATH/scoreboard.txt
echo "Copying in tips..."
sudo cp docs/tips $CCTF_PATH/tips

echo "Copying in src files..."
sudo cp -r src $CCTF_PATH/src

echo "Copying in bin files..."
sudo cp -r bin $CCTF_PATH/bin
sudo chmod 755 $CCTF_PATH/bin/*
sudo chmod 700 $CCTF_PATH/bin/testprog.py
sudo chmod 700 $CCTF_PATH/bin/scorebot.py
sudo chmod 700 $CCTF_PATH/bin/manager.py

# this is setting all the files currently in cctf (this includes all except dirs)
sudo chown -hR cctf:cctf $CCTF_PATH

echo "Creating dir directories..."
sudo mkdir $CCTF_PATH/dirs
sudo chown -h cctf:cctf $CCTF_PATH/dirs
# for each team
for i in `seq 1 $1`;
do
    sudo mkdir $CCTF_PATH/dirs/team$i
    sudo mkdir $CCTF_PATH/dirs/team$i/attacks
    sudo mkdir $CCTF_PATH/dirs/team$i/bin
    sudo mkdir $CCTF_PATH/dirs/team$i/src

    sudo chown -hR cctf:team$i $CCTF_PATH/dirs/team$i
    sudo chmod 770 $CCTF_PATH/dirs/team$i/attacks
    sudo chmod 770 $CCTF_PATH/dirs/team$i/src
    sudo chmod 775 $CCTF_PATH/dirs/team$i/bin
done


echo "Creating team home directories"
for i in `seq 1 $1`;
do
    # create team user
    id -u team$i &>/dev/null || sudo useradd team$i

    # create team home
    sudo mkdir -p $HOME_PATH/team$i
    #set home directory
    sudo usermod -d $HOME_PATH/team$i team$i

    sudo cp src/calc.c $HOME_PATH/team$i/calc.c
    sudo cp src/calc.c $HOME_PATH/team$i/calc.c.orig
    sudo chmod 640 $HOME_PATH/team$i/calc.c
    sudo chmod 440 $HOME_PATH/team$i/calc.c.orig
    sudo ln -s $CCTF_PATH/dirs/team$i/attacks $HOME_PATH/team$i/attacks

    echo "Setting TEAMS var in team$i..."
    echo "export TEAMS=$1" | sudo tee -a $HOME_PATH/team$i/.bashrc
    echo "export PATH=\"$CCTF_PATH/bin:\$PATH\"" | sudo tee -a $HOME_PATH/team$i/.bashrc
    sudo chown -h team$i:team$i $HOME_PATH/team$i/.bashrc

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
