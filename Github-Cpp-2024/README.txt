How to Extract
$$ cat *.tgz* | tar xzvf -

How to Tar & Zip & split
$$ tar czvf - filename.jsonl | split -b 59M - filename.jsonl.tgz
