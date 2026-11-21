# Dataset audit (JMuBEN, compare/dataset-coffee-leaves-images/Original)

- Files: **58,549**; byte-unique: **3,756**; distinct source patches: **861**.
- Random 75/15/10 file split (as in the old notebook): **100.0%** of test files have a byte-identical copy in train and **100.0%** have the same source patch in train.
- Duplicates with conflicting labels: {'md5_groups_with_2plus_labels': 0, 'phash_groups_with_2plus_labels': 0}.
- Splits: StratifiedGroupKFold, k=5, seed 42; SHA-256 `6e33fa0b882230b1907c2e8f1306c53112e16bf243987d2d81f24268f3a534eb`.

| cls         |   files |   byte_unique |   phash_groups |   source_groups |   files_per_source |
|:------------|--------:|--------------:|---------------:|----------------:|-------------------:|
| Miner       |   16978 |          1639 |            410 |             316 |               53.7 |
| Rust        |    8336 |          1042 |            519 |             277 |               30.1 |
| Phoma       |    6571 |           691 |            181 |             180 |               36.5 |
| Healthy     |   18983 |            62 |             14 |               9 |             2109.2 |
| Cerscospora |    7681 |           322 |             82 |              79 |               97.2 |
| Total       |   58549 |          3756 |           1206 |             861 |               68   |

Per fold:

|   fold |   train_images |   train_groups |   train_healthy_groups |   val_images |   val_groups |   val_healthy_groups |   test_images |   test_groups |   test_healthy_groups |
|-------:|---------------:|---------------:|-----------------------:|-------------:|-------------:|---------------------:|--------------:|--------------:|----------------------:|
|      0 |           2507 |            577 |                      6 |          499 |          112 |                    1 |           750 |           172 |                     2 |
|      1 |           2506 |            577 |                      6 |          500 |          113 |                    1 |           750 |           171 |                     2 |
|      2 |           2503 |            575 |                      5 |          503 |          114 |                    2 |           750 |           172 |                     2 |
|      3 |           2500 |            573 |                      7 |          499 |          114 |                    1 |           757 |           174 |                     1 |
|      4 |           2507 |            576 |                      6 |          500 |          113 |                    1 |           749 |           172 |                     2 |
