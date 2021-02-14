#!/bin/bash  

#echo "Enter the file name to encode: "  
#read filename

#cp ./backup/$filename $filename
base64 -w 0 $1 > base_enc
gzip base_enc
#rm $filename
