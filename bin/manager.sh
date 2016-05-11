#!/bin/bash
#arg1 is base directory for all team directories
#arg2 is the master attack file

while sleep 1; do
    cp $2 file.txt
    find $1 -maxdepth 1 -mindepth 1 -type d | while read i; do
        #sort by time (%T), sort by first column (time), remove first column (time), get last line
        OLDEST="$(find $i/attacks -type f -printf '%T@ %p\n' | sort -k1 | cut -d ' ' -f 1 --complement | tail -n1)"
    
        if [[ $OLDEST ]]; then
            #line="$(head -n1 $OLDEST)"
            line="$(head -n 1 "$OLDEST")"
            echo -e "TOP LINE OF OLDEST FILE: " $line '\n'
            echo "$line" >> file.txt
            rm $OLDEST
        fi
    done
    
    #remove duplicates
    sort -u file.txt > $2
    rm file.txt
    
    #TODO: run attack testing/score bot(s)
done
