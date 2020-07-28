import argparse
import logging
import multiprocessing
import os
import sys
import glob
import json

import gentle

parser = argparse.ArgumentParser(
        description='Align a transcript to audio by generating a new language model.  Outputs JSON')
parser.add_argument(
        '--nthreads', default=multiprocessing.cpu_count(), type=int,
        help='number of alignment threads')
parser.add_argument(
        '-odr', '--output_dir', type=str, 
        help='output directory')
parser.add_argument(
        '--conservative', dest='conservative', action='store_true',
        help='conservative alignment')
parser.set_defaults(conservative=False)
parser.add_argument(
        '--disfluency', dest='disfluency', action='store_true',
        help='include disfluencies (uh, um) in alignment')
parser.set_defaults(disfluency=False)
parser.add_argument(
        '--log', default="INFO",
        help='the log level (DEBUG, INFO, WARNING, ERROR, or CRITICAL)')
parser.add_argument(
        '--wav_pattern', type=str, required=True,
        help='Pattern of wav files to be aligned')
parser.add_argument(
        '--txt_pattern', type=str, required=True,
        help='Pattern of txt transcript files to be aligned (same name required)')
parser.add_argument(
        '--max_unalign', type=int, default=0.0,
        help='Maximum threshold for unalignment occurence (0.0 ~ 1.0) [default: 0.0] ')
args = parser.parse_args()

log_level = args.log.upper()
logging.getLogger().setLevel(log_level)

disfluencies = set(['uh', 'um'])

def on_progress(p):
    for k,v in p.items():
        logging.debug("%s: %s" % (k, v))

wav_paths = sorted(glob.glob(args.wav_pattern))
txt_paths = sorted(glob.glob(args.txt_pattern))    
txt_directory = '/'.join(txt_paths[0].split('/')[:-1])
txt_paths = [os.path.join(txt_directory,x.split('/')[-1].split('.')[0] + '.txt') for x in wav_paths]
txt_names = [x.split('/')[-1].split('.')[0] for x in wav_paths]
max_unalign = args.max_unalign

for input_wavfile, textfile, out_name in zip(wav_paths,txt_paths,txt_names):
    
    with open(textfile, encoding="utf-8") as fh:
        transcript = fh.read()

    resources = gentle.Resources()
    logging.info("converting audio to 8K sampled wav")

    with gentle.resampled(input_wavfile) as wavfile:
        logging.info("starting alignment")
        aligner = gentle.ForcedAligner(resources, transcript, nthreads=args.nthreads, disfluency=args.disfluency, conservative=args.conservative, disfluencies=disfluencies)
        result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)
    
    temp_result = json.loads(result.to_json())
    
    failure_count = 0
    for word in temp_result["words"]:
        case = word["case"]
        if case != "success":
            failure_count += 1 # instead of failing everything, 
            #raise RuntimeError("Alignment failed")
            continue
    unalign_ratio = float(failure_count) / len(temp_result['words'])
    print('[*] Unaligned Ratio - {}'.format(unalign_ratio))
    if unalign_ratio > max_unalign:
        print('[!] skipping this due to bad alignment')
        print()
        print('*'*100)
        print()        
        continue
            
    #fh.write(result.to_json(indent=2))
    if args.output_dir:
        fh = open(os.path.join(args.output_dir,'output_' + out_name + '.json'), 'w', encoding="utf-8")
        json.dump(result.to_json(),fh)
        print()
        logging.info("output written to %s" % (os.path.join(args.output_dir,'output_' + out_name + '.json')))
        print('*'*100)
        print()
    else:
        print()
        print('*'*100)
        print()        
        
