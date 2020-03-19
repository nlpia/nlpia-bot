""" Model used by qa_bots (forked from the simpletransformers library) """

import os
import math
import json
# import random
from multiprocessing import cpu_count
from tqdm import tqdm

import pandas as pd

# from sklearn.metrics import (
#     mean_squared_error,
#     matthews_corrcoef,
#     confusion_matrix,
#     label_ranking_average_precision_score
# )

import torch
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler, TensorDataset

from transformers import AdamW, get_linear_schedule_with_warmup
from transformers import (
    BertConfig,
    BertForQuestionAnswering,
    BertTokenizer,
    AlbertConfig,
    AlbertForQuestionAnswering,
    AlbertTokenizer
)

from .qa_utils import (
    get_examples,
    convert_examples_to_features,
    RawResult,
    write_predictions,
    # RawResultExtended,
    # write_predictions_extended,
    to_list,
    build_examples,
    get_best_predictions,
    # get_best_predictions_extended,
)

from ..constants import USE_CUDA

QABOTS_ARGS = {
    'output_dir': '',
    'cache_dir': '',
    'fp16': True,
    'fp16_opt_level': 'O2',
    'max_seq_length': 128,
    'train_batch_size': 8,
    'gradient_accumulation_steps': 1,
    'eval_batch_size': 8,
    'num_train_epochs': 2,
    'weight_decay': 0,
    'learning_rate': 4e-5,
    'adam_epsilon': 1e-8,
    'warmup_ratio': 0.06,
    'warmup_steps': 0,
    'max_grad_norm': 1.0,
    'do_lower_case': False,
    'logging_steps': 50,
    'save_steps': 2000,
    'no_cache': True,
    'save_model_every_epoch': True,
    'evaluate_during_training': True,
    'evaluate_during_training_steps': 2000,
    'use_cached_eval_features': True,
    'save_eval_checkpoints': True,
    'tensorboard_dir': None,
    'overwrite_output_dir': False,
    'reprocess_input_data': False,
    'process_count': cpu_count() - 2 if cpu_count() > 2 else 1,
    'n_gpu': 1,
    'use_multiprocessing': True,
    'silent': True
}


class QuestionAnsweringModel:
    """
    Trains and loads transformer used in question answering tasks
    Forked from https://github.com/ThilinaRajapakse/simpletransformers
    """

    def __init__(
        self, model_type, model_name_or_path,
        pretrained=True, use_cuda=USE_CUDA, cuda_device=-1, args=None
    ):
        """
        Initializes an instance of QuestionAnsweringModel

        Args:
            model_type: Identifier for which architecture to use (currently supporting Bert)
            model_name_or_path: Identifier for which architecture to download or path to saved model
            pretrained: Flag that indicates if a saved model should be loaded or will have to be trained
            use_cuda: Flag that indicates if cuda ought to be used
            cuda_device: Integer of which cuda device to use
            args: Dictionary that will update default arguments
        """
        self.args = self._get_updated_args(use_cuda, args, model_type, model_name_or_path)
        if pretrained and not os.path.exists(os.path.join(self.args['output_dir'], 'pytorch_model.bin')):
            raise ValueError(
                "pretrained=True, but pytorch_model.bin not found in {}".format(self.args['output_dir'])
            )

        model_classes = {
            'bert': (BertConfig, BertForQuestionAnswering, BertTokenizer),
            'albert': (AlbertConfig, AlbertForQuestionAnswering, AlbertTokenizer)
        }
        config_class, model_class, tokenizer_class = model_classes[model_type]

        self.model = model_class.from_pretrained(model_name_or_path)
        self.device = self._get_device(use_cuda, cuda_device)
        self.results = {}
        self.tokenizer = tokenizer_class.from_pretrained(
            model_name_or_path, do_lower_case=self.args['do_lower_case']
        )

    def train_model(self, train_data, output_dir=False, show_running_loss=True, args=None, eval_data=None):
        """
        Trains the model. Saves files to output_dir.

        Args:
            train_data: Path to JSON file containing training data
                or list of Python dicts in the correct format. The model will be trained on this data.
            output_dir: Path where model files will be saved. If not given, self.args['output_dir'] is used.
            args (optional): Optional changes to the args dict of the model. Changes will persist for model.
            eval_data (optional): Path to JSON file containing evaluation data used when
                evaluate_during_training is enabled. Required if evaluate_during_training is enabled.

        Returns:
            None
        """
        # Update self.args and perform inital checks
        if args:
            self.args.update(args)

        if self.args['evaluate_during_training'] and eval_data is None:
            raise ValueError(
                "Argument evaluate_during_training=True, but argument eval_data=None."
                " Pass eval_data to model.train_model() if using evaluate_during_training."
            )

        if not output_dir:
            output_dir = self.args['output_dir']

        if (os.path.exists(output_dir) and os.listdir(output_dir) and not self.args['overwrite_output_dir']):
            raise ValueError(
                "Output directory '{}' already exists and is not empty."
                " Set argument overwrite_output_dir=True to overwrite.".format(output_dir)
            )

        # Convert train_data to json if not already
        if isinstance(train_data, str):
            with open(train_data, 'r') as f:
                train_examples = json.load(f)
        else:
            train_examples = train_data

        # Load the training dataset
        train_dataset = self._load_and_cache_examples(train_examples)

        # Train the model and save to output_dir
        self.model.to(self.device)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        global_step, tr_loss = self._train(
            train_dataset,
            output_dir,
            show_running_loss=show_running_loss,
            eval_data=eval_data,
        )

        model_to_save = self.model.module if hasattr(self.model, 'module') else self.model
        model_to_save.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        torch.save(self.args, os.path.join(output_dir, 'training_args.bin'))

        if not self.args['silent']:
            print('Training of {} model complete. Saved to {}.'.format(self.args['model_type'], output_dir))

    def eval_model(self, eval_data, output_dir=None, verbose=False):
        """
        Evaluates the model on eval_data. Saves results to output_dir.

        Args:
            eval_data: Path to JSON file containing evaluation data OR list of Python dicts in the correct
                format. The model will be evaluated on this data.
            output_dir: Path where model files will be saved. If not given, uses self.args['output_dir'].
            verbose: If verbose, results will be printed to the console on completion of evaluation.

        Returns:
            result: Dictionary containing evaluation results. (correct, similar, incorrect)
            text: A dictionary containing the 3 dictionaries correct_text, similar_text
                 (the predicted answer is a substring of the correct answer or vise versa), incorrect_text.
        """
        if not output_dir:
            output_dir = self.args['output_dir']

        self.model.to(self.device)

        all_predictions, all_nbest_json, scores_diff_json = self._evaluate(eval_data, output_dir)

        if isinstance(eval_data, str):
            with open(eval_data, 'r') as f:
                truth = json.load(f)
        else:
            truth = eval_data

        result, texts = self.calculate_results(truth, all_predictions)

        self.results.update(result)

        if verbose:
            print(self.results)

        return result, texts

    def predict(self, to_predict, n_best_size=None):
        """
        Performs predictions on a list of python dicts containing contexts and qas.

        Args:
            to_predict: A list of dictionaries containing contexts and questions to be sent to the model
                for prediction.
                E.g: predict([
                    {
                        'context': "Some context as a demo",
                        'qas': [
                            {'id': '0', 'question': 'What is the context here?'},
                            {'id': '1', 'question': 'What is this for?'}
                        ]
                    }
                ])
            n_best_size (Optional): Number of predictions to return. args['n_best_size'] will be used if not specified.

        Returns:
            preds: A python list containg the predicted answer, and id for each question in to_predict.
        """
        # tokenizer = self.tokenizer
        device = self.device
        model = self.model
        args = self.args

        if not n_best_size:
            n_best_size = args['n_best_size']

        model.to(self.device)

        eval_examples = build_examples(to_predict)
        eval_dataset, examples, features = self._load_and_cache_examples(
            eval_examples, evaluate=True, output_examples=True, no_cache=True
        )

        eval_sampler = SequentialSampler(eval_dataset)
        eval_dataloader = DataLoader(
            eval_dataset, sampler=eval_sampler, batch_size=args['eval_batch_size']
        )

        all_results = []

        model.eval()
        for batch in tqdm(eval_dataloader, disable=args['silent']):
            batch = tuple(t.to(device) for t in batch)

            with torch.no_grad():
                inputs = {
                    'input_ids': batch[0],
                    'attention_mask': batch[1]
                }

                if args['model_type'] != 'distilbert':
                    inputs['token_type_ids'] = batch[2]

                example_indices = batch[3]

                outputs = model(**inputs)

                for i, example_index in enumerate(example_indices):
                    eval_feature = features[example_index.item()]
                    unique_id = int(eval_feature.unique_id)
                    result = RawResult(
                        unique_id=unique_id,
                        start_logits=to_list(outputs[0][i]),
                        end_logits=to_list(outputs[1][i]),
                    )
                    all_results.append(result)

        answers = get_best_predictions(
            examples,
            features,
            all_results,
            n_best_size,
            args['max_answer_length'],
            False,
            False,
            True,
            False,
        )

        return answers

    def calculate_results(self, truth, predictions):
        """
        TODO
        """
        truth_dict = {}
        questions_dict = {}
        for item in truth:
            for answer in item['qas']:
                if answer['answers']:
                    truth_dict[answer['id']] = answer['answers'][0]['text']
                else:
                    truth_dict[answer['id']] = ''
                questions_dict[answer['id']] = answer['question']

        correct = 0
        incorrect = 0
        similar = 0
        correct_text = {}
        incorrect_text = {}
        similar_text = {}
        for q_id, answer in truth_dict.items():
            if predictions[q_id].strip() == answer.strip():
                correct += 1
                correct_text[q_id] = answer
            elif (
                predictions[q_id].strip() in answer.strip() or
                answer.strip() in predictions[q_id].strip()
            ):
                similar += 1
                similar_text[q_id] = {
                    'truth': answer,
                    'predicted': predictions[q_id],
                    'question': questions_dict[q_id],
                }
            else:
                incorrect += 1
                incorrect_text[q_id] = {
                    'truth': answer,
                    'predicted': predictions[q_id],
                    'question': questions_dict[q_id],
                }

        result = {
            'correct': correct,
            'similar': similar,
            'incorrect': incorrect,
        }

        texts = {
            'correct_text': correct_text,
            'similar_text': similar_text,
            'incorrect_text': incorrect_text,
        }

        return result, texts

    ''' Utility Methods '''

    def _get_device(self, use_cuda, cuda_device):
        """
        Utility method called from constructor
        Args:
            use_cuda:
            cuda_device:
        Returns:
            device:
        """
        if use_cuda:
            if torch.cuda.is_available():
                if cuda_device == -1:
                    device = torch.device('cuda')
                else:
                    device = torch.device(f'cuda:{cuda_device}')
            else:
                raise ValueError(
                    "Argument use_cuda=True when cuda is unavailable."
                    " Make sure cuda is available or set use_cuda=False."
                )
                raise ValueError('Arg: \'use_cuda\' set to True when cuda is unavailable.')
        else:
            device = 'cpu'
        return device

    def _get_updated_args(self, use_cuda, args, model_type, model_name_or_path):
        updated_args = {
            'doc_stride': 384,
            'max_query_length': 64,
            'n_best_size': 20,
            'max_answer_length': 100,
            'null_score_diff_threshold': 0.0
        }

        updated_args.update(QABOTS_ARGS)

        if not use_cuda:
            updated_args['fp16'] = False

        if args:
            updated_args.update(args)

        updated_args['model_type'] = model_type
        updated_args['model_name_or_path'] = model_name_or_path

        return updated_args

    def _load_and_cache_examples(self, examples, evaluate=False, no_cache=False, output_examples=False):
        tokenizer = self.tokenizer
        args = self.args
        no_cache = args['no_cache']

        if not os.path.isdir(self.args['cache_dir']):
            os.mkdir(self.args['cache_dir'])

        # preprocess examples into an InputExample list
        examples = get_examples(examples, is_training=not evaluate)

        mode = 'dev' if evaluate else 'train'
        cached_features_file = os.path.join(
            args['cache_dir'],
            'cached_{}_{}_{}_{}'.format(
                mode, args['model_type'], args['max_seq_length'], len(examples)
            )
        )

        # get features
        if os.path.exists(cached_features_file) and (
            (not args['reprocess_input_data'] and not no_cache) or
            (mode == 'dev' and args['use_cached_eval_features'])
        ):
            features = torch.load(cached_features_file)
            if not args['silent']:
                print(f'Features loaded from cache at {cached_features_file}')
        else:
            if not args['silent']:
                print(f'Converting to features . . .')
            features = convert_examples_to_features(
                examples=examples,
                tokenizer=tokenizer,
                max_seq_length=args['max_seq_length'],
                doc_stride=args['doc_stride'],
                max_query_length=args['max_query_length'],
                is_training=not evaluate,
                cls_token_segment_id=0,
                pad_token_segment_id=0,
                cls_token_at_end=False,
                sequence_a_is_doc=False,
                silent=args['silent']
            )
            if not no_cache:
                torch.save(features, cached_features_file)

        # extract data from features
        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor(
            [f.input_mask for f in features], dtype=torch.long
        )
        all_segment_ids = torch.tensor(
            [f.segment_ids for f in features], dtype=torch.long
        )
        all_cls_index = torch.tensor([f.cls_index for f in features], dtype=torch.long)
        all_p_mask = torch.tensor([f.p_mask for f in features], dtype=torch.float)
        all_example_index = torch.arange(all_input_ids.size(0), dtype=torch.long)

        # build TensorDataset from data extracted from features
        if evaluate:
            dataset = TensorDataset(
                all_input_ids,
                all_input_mask,
                all_segment_ids,
                all_example_index,
                all_cls_index,
                all_p_mask,
            )
        else:
            all_start_positions = torch.tensor(
                [f.start_position for f in features], dtype=torch.long
            )
            all_end_positions = torch.tensor(
                [f.end_position for f in features], dtype=torch.long
            )
            dataset = TensorDataset(
                all_input_ids,
                all_input_mask,
                all_segment_ids,
                all_start_positions,
                all_end_positions,
                all_cls_index,
                all_p_mask,
            )

        if output_examples:
            return dataset, examples, features
        return dataset

    def _train(self, train_dataset, output_dir, show_running_loss=True, eval_data=None):
        device = self.device
        model = self.model
        args = self.args

        # setup DataLoader
        train_sampler = RandomSampler(train_dataset)
        train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=args['train_batch_size'])

        # setup optimizer + scheduler
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
             'weight_decay': args['weight_decay']},
            {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
             'weight_decay': 0.0}
        ]

        t_total = len(train_dataloader) // args['gradient_accumulation_steps'] * args['num_train_epochs']
        warmup_steps = math.ceil(t_total * args['warmup_ratio'])
        args['warmup_steps'] = warmup_steps if args['warmup_steps'] == 0 else args['warmup_steps']

        optimizer = AdamW(optimizer_grouped_parameters, lr=args['learning_rate'], eps=args['adam_epsilon'])
        scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps=args['warmup_steps'], num_training_steps=t_total)

        # setup mixed precision training and data parallelism
        if args['fp16']:
            try:
                from apex import amp
            except ImportError:
                raise ImportError('Argument fp16=True but the apex library is not installed')
            model, optimizer = amp.initialize(model, optimizer, opt_level=args['fp16_opt_level'])

        if args['n_gpu'] > 1:
            model = torch.nn.DataParallel(model)

        # zero epoch, steps, loss, model's gradient, and training history
        epoch_number = 0
        global_step = 0
        tr_loss = 0.0
        # logging_loss = 0.0
        model.zero_grad()
        trange = range
        train_iterator = trange(int(args['num_train_epochs']), desc='Epoch', disable=args['silent'])
        if args['evaluate_during_training']:
            training_progress_scores = {
                'global_step': [],
                'correct': [],
                'similar': [],
                'incorrect': [],
                'train_loss': [],
            }

        # pytorch training loop
        model.train()
        for _ in train_iterator:
            for step, batch in enumerate(tqdm(train_dataloader, desc='Current iteration', disable=args['silent'])):
                # load batch to device
                batch = tuple(t.to(device) for t in batch)
                inputs = {
                    'input_ids': batch[0],
                    'attention_mask': batch[1],
                    'start_positions': batch[3],
                    'end_positions': batch[4],
                }

                # assign token_type_ids
                if args['model_type'] != 'distilbert':
                    inputs['token_type_ids'] = batch[2]

                # get output tuple from the model
                outputs = model(**inputs)
                loss = outputs[0]
                if args['n_gpu'] > 1:
                    loss = loss.mean()
                current_loss = loss.item()
                if show_running_loss:
                    print('\rRunning loss: %f' % loss, end='')
                if args['gradient_accumulation_steps'] > 1:
                    loss = loss / args['gradient_accumulation_steps']

                # perform backprop and gradient clipping
                if args['fp16']:
                    with amp.scale_loss(loss, optimizer) as scaled_loss:
                        scaled_loss.backward()
                    torch.nn.utils.clip_grad_norm_(amp.master_params(optimizer), args['max_grad_norm'])
                else:
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), args['max_grad_norm'])

                # TODO . . .
                tr_loss += loss.item()
                if (step + 1) % args['gradient_accumulation_steps'] == 0:
                    optimizer.step()
                    scheduler.step()
                    model.zero_grad()
                    global_step += 1

                    # TODO log metrics after the step

                    # save model checkpoint
                    if args['save_steps'] > 0 and global_step % args['save_steps'] == 0:
                        output_dir_current = os.path.join(output_dir, 'checkpoint-{}'.format(global_step))
                        if not os.path.exists(output_dir_current):
                            os.makedirs(output_dir_current)
                        model_to_save = model.module if hasattr(model, "module") else model
                        model_to_save.save_pretrained(output_dir_current)
                        self.tokenizer.save_pretrained(output_dir_current)

                    # evaluate the model
                    if (args['evaluate_during_training'] and args['evaluate_during_training_steps'] > 0 and
                            global_step % args['evaluate_during_training_steps'] == 0):
                        results, _ = self.eval_model(eval_data, verbose=True)

                        output_dir_current = os.path.join(output_dir, 'checkpoint-{}'.format(global_step))

                        if not os.path.exists(output_dir_current):
                            os.makedirs(output_dir_current)

                        if args['save_eval_checkpoints']:
                            model_to_save = model.module if hasattr(model, 'module') else model
                            model_to_save.save_pretrained(output_dir_current)
                            self.tokenizer.save_pretrained(output_dir_current)

                        output_eval_file = os.path.join(output_dir_current, 'eval_results.txt')
                        with open(output_eval_file, 'w') as writer:
                            for key in sorted(results.keys()):
                                writer.write('{} = {}\n'.format(key, str(results[key])))

                        training_progress_scores['global_step'].append(global_step)
                        training_progress_scores['train_loss'].append(current_loss)
                        for key in results:
                            training_progress_scores[key].append(results[key])
                        report = pd.DataFrame(training_progress_scores)
                        report.to_csv(args['output_dir'] + 'training_progress_scores.csv', index=False)

            epoch_number += 1
            output_dir_current = os.path.join(output_dir, 'checkpoint-{}-epoch-{}'.format(global_step, epoch_number))

            if args['save_model_every_epoch'] or args['evaluate_during_training'] and not os.path.exists(output_dir_current):
                os.makedirs(output_dir_current)

            if args['save_model_every_epoch']:
                model_to_save = model.module if hasattr(model, 'module') else model
                model_to_save.save_pretrained(output_dir_current)
                self.tokenizer.save_pretrained(output_dir_current)

            if args['evaluate_during_training']:
                results, _ = self.eval_model(eval_data, verbose=True)
                output_eval_file = os.path.join(output_dir_current, 'eval_results.txt')
                with open(output_eval_file, 'w') as writer:
                    for key in sorted(results.keys()):
                        writer.write('{} = {}\n'.format(key, str(results[key])))

        return global_step, tr_loss / global_step

    def _evaluate(self, eval_data, output_dir):
        """
        Utility method that evaluates the model on eval_data. Called by the eval_model() method
        """
        tokenizer = self.tokenizer  # noqa
        device = self.device
        model = self.model
        args = self.args

        if isinstance(eval_data, str):
            with open(eval_data, 'r') as f:
                eval_examples = json.load(f)
        else:
            eval_examples = eval_data

        eval_dataset, examples, features = self._load_and_cache_examples(
            eval_examples, evaluate=True, output_examples=True
        )

        eval_sampler = SequentialSampler(eval_dataset)
        eval_dataloader = DataLoader(
            eval_dataset, sampler=eval_sampler, batch_size=args['eval_batch_size']
        )

        all_results = []

        # pytorch evaluation loop
        model.eval()
        for batch in tqdm(eval_dataloader, disable=args['silent']):
            batch = tuple(t.to(device) for t in batch)

            with torch.no_grad():
                inputs = {
                    'input_ids': batch[0],
                    'attention_mask': batch[1],
                }

                if args['model_type'] != 'distilbert':
                    inputs["token_type_ids"] = None if args["model_type"] == "xlm" else batch[2]

                example_indices = batch[3]

                outputs = model(**inputs)

                for i, example_index in enumerate(example_indices):
                    eval_feature = features[example_index.item()]
                    unique_id = int(eval_feature.unique_id)
                    result = RawResult(
                        unique_id=unique_id,
                        start_logits=to_list(outputs[0][i]),
                        end_logits=to_list(outputs[1][i]),
                    )
                    all_results.append(result)

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        output_prediction_file = os.path.join(output_dir, 'predictions_{}.json'.format('test'))
        output_nbest_file = os.path.join(output_dir, 'nbest_predictions_{}.json'.format('test'))
        output_null_log_odds_file = os.path.join(output_dir, 'null_odds_{}.json'.format('test'))

        all_predictions, all_nbest_json, scores_diff_json = write_predictions(
            examples,
            features,
            all_results,
            args['n_best_size'],
            args['max_answer_length'],
            False,
            output_prediction_file,
            output_nbest_file,
            output_null_log_odds_file,
            not args['silent'],
            True,
            args['null_score_diff_threshold']
        )

        return all_predictions, all_nbest_json, scores_diff_json
