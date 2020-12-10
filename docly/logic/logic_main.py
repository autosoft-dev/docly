import os
import sys
from io import open

import numpy as np
import torch
import torch.nn as nn

from .example import make_example, make_new_example
from .input_features import convert_examples_to_features
from torch.utils.data import DataLoader, Dataset, SequentialSampler, TensorDataset

from transformers import (WEIGHTS_NAME, AdamW, get_linear_schedule_with_warmup,
                          RobertaConfig, RobertaModel, RobertaTokenizer)


MODEL_CLASSES = {'roberta': (RobertaConfig, RobertaModel, RobertaTokenizer)}

model_name_or_path = "microsoft/codebert-base"
beam_size = 10
max_target_length = 128
max_source_length = 256
seed = 42


def load_model(model_path, is_old=False):
    if is_old:
        from .model import Seq2Seq
    else:
        from .model_new import Seq2Seq
    
    config_class, model_class, tokenizer_class = MODEL_CLASSES['roberta']
    
    config = config_class.from_pretrained(model_name_or_path)
    if is_old:
        tokenizer = tokenizer_class.from_pretrained(model_name_or_path)
    else:
        tokenizer = tokenizer_class.from_pretrained(model_name_or_path, do_lower_case=False)

    encoder = model_class.from_pretrained(model_name_or_path, config=config)  
    decoder_layer = nn.TransformerDecoderLayer(d_model=config.hidden_size, 
                                               nhead=config.num_attention_heads)
    decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
    model = Seq2Seq(encoder=encoder,
                    decoder=decoder,
                    config=config,
                    beam_size=beam_size,
                    max_length=max_target_length,
                    sos_id=tokenizer.cls_token_id,
                    eos_id=tokenizer.sep_token_id
                   )
    if is_old:
        if not torch.cuda.is_available():
            model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        else:
            model.load_state_dict(torch.load(model_path))
    else:
        if not torch.cuda.is_available():
            model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')), strict=False)
        else:
            model.load_state_dict(torch.load(model_path), strict=False)
    if not torch.cuda.is_available():
        model.to("cpu")
    model.eval()

    return model, tokenizer


def predict_docstring(model, tokenizer, code_tokens, is_old):
    examples = make_example(code_tokens) if is_old else make_new_example(code_tokens)

    features = convert_examples_to_features(examples, tokenizer)
    if is_old:
        all_source_ids = torch.tensor([f.source_ids for f in features], dtype=torch.long)
        all_source_mask = torch.tensor([f.source_mask for f in features], dtype=torch.long)
    else:
        all_source_ids = torch.tensor([f.source_ids[: max_source_length] for f in features], dtype=torch.long)
        all_source_mask = torch.tensor([f.source_mask[: max_source_length] for f in features], dtype=torch.long)

    eval_data = TensorDataset(all_source_ids, all_source_mask)

    eval_sampler = SequentialSampler(eval_data)
    batch_size = len(code_tokens) if is_old else len(eval_data)

    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=batch_size)

    p=[]
    for batch in eval_dataloader:
        if not torch.cuda.is_available():
            batch = tuple(t.to('cpu') for t in batch)
        else:
            batch = tuple(t for t in batch)
        source_ids, source_mask = batch

        with torch.no_grad():
            preds = model(source_ids=source_ids, source_mask=source_mask)

            for pred in preds:
                t=pred[0].cpu().numpy()
                t=list(t)
                if 0 in t:
                    t=t[:t.index(0)]
                text = tokenizer.decode(t,clean_up_tokenization_spaces=False)
                p.append(text)
    
    px = p[0].split()
    if px[-1] == ".":
        px[-2] = px[-2].strip() + "."
        px.pop()
    
    return [" ".join(px)]
