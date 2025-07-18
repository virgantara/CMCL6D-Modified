#!/bin/bash

set -x
set -e

export PYTHONUNBUFFERED="True"
export PYTHONWARNINGS="ignore"

export CUDA_VISIBLE_DEVICES=0
#export CUDA_VISIBLE_DEVICES=1
#export CUDA_VISIBLE_DEVICES=2
#export CUDA_VISIBLE_DEVICES=3
export PYTHONPATH=$(pwd):$PYTHONPATH
echo "PYTHONPATH = $PYTHONPATH"
start=`date +%s`
    
python3 ./tools/train.py --nepoch 2 --dataset ycb\
  --dataset_root ./datasets/ycb/YCB_Video_Dataset

end=`date +%s`

runtime=$((end-start))
echo $runtime