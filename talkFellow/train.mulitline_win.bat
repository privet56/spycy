cd ../../3rdparty_libs/seq2seq

python -m bin.train ^
--batch_size 1024 --eval_every_n_steps 5000 ^
--train_steps 5000000 ^
--output_dir ../../spycy/talkFellow/data_ger_partitur/model ^
--config_paths="./example_configs/nmt_large.yml,./example_configs/train_seq2seq.yml,../../spycy/talkFellow/data_ger_partitur/conversations_train_config.yml"
