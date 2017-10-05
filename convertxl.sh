cd /Directory
for f in *.xlsx; do ssconvert "$f" "${f%.csv}.csv"; done