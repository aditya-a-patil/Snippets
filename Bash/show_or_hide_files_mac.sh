#!/bin/bash
if [ -z "$1" ]; then 
	echo usage: $0 \<show or hide\>
	exit
fi
if [ "$1" = "show" ]; then
	defaults write com.apple.finder AppleShowAllFiles YES
else
	defaults write com.apple.finder AppleShowAllFiles NO
fi
killall Finder /System/Library/CoreServices/Finder.app
