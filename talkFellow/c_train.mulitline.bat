cd ../../3rdparty_libs/seq2seq

python -m bin.train \
--config_paths="
./example_configs/nmt_large.yml,
./example_configs/train_seq2seq.yml" \
--model_params "
vocab_source: ../../spycy/talkFellow/data/gutenberg.tok
vocab_target: ../../spycy/talkFellow/data/gutenberg.tok" \
--input_pipeline_train "
class: ParallelTextInputPipeline
params:
source_files:
- ../../spycy/talkFellow/data/train/sources.txt
target_files:
- ../../spycy/talkFellow/data/train/targets.txt" \
--input_pipeline_dev "
class: ParallelTextInputPipeline
params:
source_files:
- ../../spycy/talkFellow/data/dev/sources.txt
target_files:
- ../../spycy/talkFellow/data/dev/targets.txt" \
--batch_size 1024 --eval_every_n_steps 5000 \
--train_steps 5000000 \
--output_dir ../../spycy/talkFellow/data/model
