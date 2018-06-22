#!/bin/bash

for i in `seq -f %02g 27 40`
do
	fname="$(ls "../../tweets/newsEN-20180508/json/parts30min/" | grep "part${i}-")"
	tn="../../tweets/newsEN-20180508/json/parts30min/${fname}"
	echo $tn
	time ./main.py -a "$tn" "../../tweets/newsEN-20180508/topics/parts30minBIS/$(basename "$fname" '.json')/"
done
