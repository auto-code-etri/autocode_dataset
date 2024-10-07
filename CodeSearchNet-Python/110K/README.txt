How to Extract
$$ cat *.tgz* | tar xzvf -

How to Tar & Zip
$$ tar czvf - train_augment.jsonl | split -b 49M - train_augment.jsonl.tgz
