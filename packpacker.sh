#!/usr/bin/env bash

CWD=`pwd`
PACK=`basename "$1"`
SLUG=`basename "$1" | sed -e "s/ /-/" | tr '[:upper:]' '[:lower:]'`
UUID=`uuidgen`
echo -e "Generating ${PACK}.pack"

cd $1

echo -e '<?xml version="1.0" encoding="utf-8" standalone="no"?>' > pack.xml
echo -e "<pack id=\"${UUID}\">" >> pack.xml
echo -e "\t<name>${PACK}</name>" >> pack.xml
echo -e "\t<slug>${SLUG}</slug>" >> pack.xml
echo -e "\t<description></description>" >> pack.xml
echo -e "\t<author></author>" >> pack.xml
echo -e "\t<code></code>" >> pack.xml
echo -e "\t<category>personal</category>" >> pack.xml
echo -e "\t<image></image>" >> pack.xml
for file in ./*.*
do
	BNAME=`basename $file`
	RNAME="${BNAME%.*}"
	if [ "${filename##*.}" != ".xml" ]
	then
		UUID=`uuidgen`
		echo -e "\t<asset id=\"${UUID}\">" >> pack.xml
		echo -e "\t\t<name>${RNAME}</name>" >> pack.xml
		echo -e "\t\t<resource>${BNAME}</resource>" >> pack.xml
		echo -e "\t\t<type>image</type>" >> pack.xml
		echo -e "\t\t<size></size>" >> pack.xml
		echo -e "\t</asset>" >> pack.xml
	fi
done
echo -e "</pack>" >> pack.xml
zip "../${PACK}.zip" *.*
cd ..
mv "${PACK}.zip" "${PACK}.pack"
