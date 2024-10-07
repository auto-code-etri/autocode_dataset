How to Extract
$$ cat *.tgz* | tar xzvf -

How to Tar & Zip
$$ tar czvf - train_augment3.jsonl | split -b 100M - train_augment3.jsonl.tgz
