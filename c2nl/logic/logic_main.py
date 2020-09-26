from typing import List

import torch
from torch.utils.data.sampler import SequentialSampler
from torch.utils.data import DataLoader

from .dataset import CommentDataset
from .model import Code2NaturalLanguage
from .symbolic import filter_translation_output
from c2nl.objects import Code
from c2nl.inputters.dataset import CommentDataset as CommentDataset
from c2nl.inputters.vector import batchify
from c2nl.utils.copy_utils import collapse_copy_scores as collapse_copy_scores
from c2nl.utils.copy_utils import make_src_map as make_src_map
from c2nl.translator.beam import GNMTGlobalScorer
from c2nl.translator.translation import TranslationBuilder
from c2nl.translator.translator import Translator



def load_model(model_path: str):
    return Code2NaturalLanguage.load(model_path)


def prepare_batch(batch, model):
    # To enable copy attn, collect source map and alignment info
    batch_inputs = dict()

    if model.args.copy_attn:
        assert 'src_map' in batch and 'alignment' in batch
        source_map = make_src_map(batch['src_map'])
        alignment = None
        blank, fill = collapse_copy_scores(model.tgt_dict, batch['src_vocab'])
    else:
        source_map, alignment = None, None
        blank, fill = None, None

    batch_inputs['src_map'] = source_map
    batch_inputs['alignment'] = alignment
    batch_inputs['blank'] = blank
    batch_inputs['fill'] = fill

    code_word_rep = batch['code_word_rep']
    code_char_rep = batch['code_char_rep']
    code_type_rep = batch['code_type_rep']
    code_mask_rep = batch['code_mask_rep']
    code_len = batch['code_len']

    batch_inputs['code_word_rep'] = code_word_rep
    batch_inputs['code_char_rep'] = code_char_rep
    batch_inputs['code_type_rep'] = code_type_rep
    batch_inputs['code_mask_rep'] = code_mask_rep
    batch_inputs['code_len'] = code_len
    return batch_inputs


def predict_docstring(model: Code2NaturalLanguage, code_tokens: List[str], raw_code: str):
    code = Code()
    code.tokens = code_tokens
    code.text = raw_code

    scorer = GNMTGlobalScorer(0.0, 0.0, None, None)
    translator = Translator(model, 
                            False, 
                            beam_size=4, 
                            n_best=1, 
                            max_length=50, 
                            copy_attn=model.args.copy_attn,
                            global_scorer=scorer,
                            min_length=2,
                            stepwise_penalty=False,
                            block_ngram_repeat=1,
                            ignore_when_blocking=[],
                            replace_unk=True)
    builder = TranslationBuilder(model.tgt_dict, n_best=1, replace_unk=True)

    dataset = CommentDataset([{"code": code, "summary": None}], model)
    sampler = SequentialSampler(dataset)

    data_loader = DataLoader(dataset,
                             batch_size=1,
                             sampler=sampler, 
                             num_workers=1, 
                             collate_fn=batchify, 
                             pin_memory=False, 
                             drop_last=False)
    for ex in data_loader:
        batch_size = ex['batch_size']
        ids = list(range (batch_size,
                         batch_size + batch_size))
        batch_inputs = prepare_batch(ex, model)
        ret = translator.translate_batch(batch_inputs)
        targets = [[summ] for summ in ex['summ_text']]
        translation = builder.from_batch(ret, ex['code_tokens'], targets, ex['src_vocab'])
        return " ".join(filter_translation_output(translation[0].pred_sents[0]))
