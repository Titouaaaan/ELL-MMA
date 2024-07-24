#-*- coding: utf-8 -*-
"""
@authors:aniruddha-adhikary,Mahir Labib Chowdhury
source:https://github.com/banglakit/number-to-bengali-word/blob/main/number_to_bengali/utils.py
"""
from __future__ import print_function
import enum
import math 
#-------------------------------------------
# globals
#-------------------------------------------
from .words import numeric_words,numbers,units

#-------------------------------------------
# helpers
#-------------------------------------------
def input_sanitizer(number):
    '''
        sanitizes an input
    '''
    if isinstance(number, float) or isinstance(number, int) or \
            isinstance(number, str):
        if isinstance(number, str):
            try:
                if "." in number:
                    number = float(number)
                else:
                    number = int(number)
            except ValueError:
                return None
        return number
    else:
        return None

def generate_segments(number):
    """
    Generating the unit segments such as koti, lokkho
    """
    segments = dict()
    segments['koti'] = math.floor(number/10000000)
    number = number % 10000000
    segments['lokkho'] = math.floor(number/100000)
    number = number % 100000
    segments['hazar'] = math.floor(number/1000)
    number = number % 1000
    segments['sotok'] = math.floor(number/100)
    number = number % 100
    segments['ekok'] = number
    return segments

def whole_part_word_gen(segments):
    """
    Generating the bengali word for the whole part of the number
    """
    generated_words = ''
    for segment in segments:
        if segments[segment]:
            generated_words += numeric_words[str(segments[segment])] + \
                " " + units[segment] + " "

    return generated_words[:-2]


def fraction_to_words(fraction):
    """
    Generating bengali words for the part after the decimal point
    """
    generated_words = ""
    for digit in str(fraction):
        generated_words += numeric_words[digit] + " "
    return generated_words[:-1]

def float_int_extraction(number):
    """
    Extracting the float and int part from the passed number. The first return
    is the part before the decimal point and the rest is the fraction.
    """
    _number = str(number)
    if "." in _number:
        return tuple([int(x) for x in _number.split(".")])
    else:
        return number, None


def to_bn_word(number):
    """
    Takes a number and outputs the word form in Bengali for that number.
    """

    generated_words = ""
    
    number=input_sanitizer(number)

    whole, fraction = float_int_extraction(number)

    whole_segments = generate_segments(whole)

    generated_words = whole_part_word_gen(whole_segments)

    if fraction:
        if generated_words:
            return generated_words + " দশমিক " + fraction_to_words(fraction)
        else:
            return "দশমিক " + fraction_to_words(fraction)
    else:
        return generated_words

#---------------------------------------------------------
def numerize(text):
    '''
        numerizes a given bangla text 
    ''' 
    # extract numbers
    nums=[]
    num=''
    for idx,n in enumerate(text):
        if n in numbers:
            num+=n
        else:
            nums.append(num)
            num='' 
    nums.append(num)
    nums=[n for n in nums if n!='']

    # converting to ennums
    numdata=[]
    for n in nums:
        ennum=''
        for i in n:
            if i!='.':
                ennum+=str(numbers.index(i))
            else:
                ennum+=i 
        numdata.append((n,to_bn_word(ennum)))

    # replacing text data
    for k in numdata:
        n,v=k
        text=text.replace(n,v)     
    return text


