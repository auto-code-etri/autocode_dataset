How to Extract
$$ cat *.tgz* | tar xzvf -

How to Tar & Zip
$$ tar czvf - train_augment2.jsonl | split -b 100M - train_augment2.jsonl.tgz
