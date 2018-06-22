#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# SentiStrength interface
# This code launches SentiStrength on all provided texts
#
# SentiStrength created by M. Thelwall et al., University of Wolverhampton, UK
# This script was written by Quentin Ribac, May 2018

import subprocess

def rate(texts):
    # remove newlines and replace space with plus in input texts
    for i in range(len(texts)):
        texts[i] = texts[i].replace('\n', '+')
        texts[i] = texts[i].replace(' ', '+')
        texts[i] = texts[i].lstrip('+')
        texts[i] = texts[i].rstrip('+')

    # launch SentiStrength in a subprocess
    res = subprocess.run('java -jar ./SentiStrength/SentiStrengthCom.jar scale stdin sentidata ./SentiStrength/SentiStrength_DataEnglishFeb2017/'.split(' '), input = '\n'.join(texts), stdout = subprocess.PIPE, encoding = 'utf-8')

    # process output
    output = res.stdout.split('\n')
    output = [line.split('\t')[:-1] for line in output if len(line) > 0]
    output = [[int(val) for val in line] for line in output]
    output = [line[2] for line in output]
    
    return output
