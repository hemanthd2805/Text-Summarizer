import nltk
import pyttsx3
import os
import re
import math
import operator
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize,word_tokenize
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
from pdfminer.high_level import extract_text
Stopwords = set(stopwords.words('english'))
wordlemmatizer = WordNetLemmatizer()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
voiceRate = 190
engine.setProperty('rate',voiceRate)

def speak(summary,filename):
    #engine.say(audio)
    engine.save_to_file(summary,filename)
    engine.runAndWait()

def lemmatize_words(words):
    lemmatized_words = []
    for word in words:
       lemmatized_words.append(wordlemmatizer.lemmatize(word))
    return lemmatized_words

def remove_special_characters(text):
    regex = r'[^a-zA-Z0-9\s]'
    text = re.sub(regex,'',text)
    return text

def freq(words):
    words = [word.lower() for word in words]
    dict_freq = {}
    words_unique = []
    for word in words:
       if word not in words_unique:
           words_unique.append(word)
    for word in words_unique:
       dict_freq[word] = words.count(word)
    return dict_freq

def pos_tagging(text):
    pos_tag = nltk.pos_tag(text.split())
    pos_tagged_noun_verb = []
    for word,tag in pos_tag:
        if tag == "NN" or tag == "NNP" or tag == "NNS" or tag == "VB" or tag == "VBD" or tag == "VBG" or tag == "VBN" or tag == "VBP" or tag == "VBZ":
             pos_tagged_noun_verb.append(word)
    return pos_tagged_noun_verb

def tf_score(word,sentence):
    freq_sum = 0
    word_frequency_in_sentence = 0
    len_sentence = len(sentence)
    for word_in_sentence in sentence.split():
        if word == word_in_sentence:
            word_frequency_in_sentence = word_frequency_in_sentence + 1
    tf =  word_frequency_in_sentence/ len_sentence
    return tf

def idf_score(no_of_sentences,word,sentences):
    no_of_sentence_containing_word = 0
    for sentence in sentences:
        sentence = remove_special_characters(str(sentence))
        sentence = re.sub(r'\d+', '', sentence)
        sentence = sentence.split()
        sentence = [word for word in sentence if word.lower() not in Stopwords and len(word)>1]
        sentence = [word.lower() for word in sentence]
        sentence = [wordlemmatizer.lemmatize(word) for word in sentence]
        if word in sentence:
            no_of_sentence_containing_word = no_of_sentence_containing_word + 1
    idf = math.log10(no_of_sentences/no_of_sentence_containing_word)
    return idf

def tf_idf_score(tf,idf):
    return tf*idf

def word_tfidf(dict_freq,word,sentences,sentence):
    word_tfidf = []
    tf = tf_score(word,sentence)
    idf = idf_score(len(sentences),word,sentences)
    tf_idf = tf_idf_score(tf,idf)
    return tf_idf

def sentence_importance(sentence,dict_freq,sentences):
     sentence_score = 0
     sentence = remove_special_characters(str(sentence))
     sentence = re.sub(r'\d+', '', sentence)
     pos_tagged_sentence = []
     no_of_sentences = len(sentences)
     pos_tagged_sentence = pos_tagging(sentence)
     for word in pos_tagged_sentence:
          if word.lower() not in Stopwords and word not in Stopwords and len(word)>1:
                word = word.lower()
                word = wordlemmatizer.lemmatize(word)
                sentence_score = sentence_score + word_tfidf(dict_freq,word,sentences,sentence)
     return sentence_score

def run_summarization(text,percent):
    tokenized_sentence = sent_tokenize(text)
    text = remove_special_characters(str(text))
    text = re.sub(r'\d+', '', text)
    tokenized_words_with_stopwords = word_tokenize(text)
    print("Total no. of words: ", len(tokenized_words_with_stopwords))
    tokenized_words = [word for word in tokenized_words_with_stopwords if word not in Stopwords]
    print("Without stopwords: ",len(tokenized_words))
    tokenized_words = [word for word in tokenized_words if len(word) > 1]
    print("With more than one letter: ",len(tokenized_words))
    tokenized_words = [word.lower() for word in tokenized_words]
    tokenized_words = lemmatize_words(tokenized_words)
    print("Words: ", tokenized_words)
    print("Frequency of each word:")
    word_freq = freq(tokenized_words)
    print(word_freq)
    no_of_sentences = int((percent * len(tokenized_sentence))/100)
    c = 1
    sentence_with_importance = {}
    for sent in tokenized_sentence:
        sentenceimp = sentence_importance(sent,word_freq,tokenized_sentence)
        sentence_with_importance[c] = sentenceimp
        c = c+1
    print("Sentence number with tf-idf scores: ")
    print(sentence_with_importance)
    sentence_with_importance = sorted(sentence_with_importance.items(), key=operator.itemgetter(1),reverse=True)
    cnt = 0
    summary = []
    sentence_no = []
    for word_prob in sentence_with_importance:
        if cnt < no_of_sentences:
            sentence_no.append(word_prob[0])
            cnt = cnt+1
        else:
          break
    sentence_no.sort()
    cnt = 1
    for sentence in tokenized_sentence:
        if cnt in sentence_no:
           summary.append(sentence)
        cnt = cnt+1
    summary = " ".join(summary)
    return summary

def startexec(filenames,inputpercent):
    result = ''
    count = 0
    percent = int(inputpercent.get())
    for filen in filenames:
        count += 1
        text = extract_text(filen)
        text = text.replace('\n','')
        result += '\n\n\nDocument no. ' + str(count) + ': ' + str(filen) + '\n'
        summary = run_summarization(text,percent)
        result += summary
        name,type = os.path.splitext(filen)
        nameOfFile = os.path.basename(name)
        nameFinal = nameOfFile+'.mp3'
        speak(summary,nameFinal)
    msg = Text(App, height=33, width=120)
    msg.place(relx=0.5, rely=0.6, anchor=CENTER)
    msg.insert(tkinter.END, result)

def select_file():
    filetypes = (
        ('pdf files', '*.pdf'),
        ('All files', '*.*')
    )
    filenames = filedialog.askopenfilenames(
        title='Open a file',
        initialdir='/"Python files"/summary',
        filetypes=filetypes)
    labelpercent = Label(App, text="Enter the percentage")
    labelpercent.place(relx=0.4,rely=0.2,anchor=CENTER)
    inputpercent = Entry(App)
    inputpercent.insert(tkinter.END,'50')
    inputpercent.place(relx=0.5,rely=0.2,anchor=CENTER)
    start = Button(App, text='Start', command = lambda: startexec(filenames,inputpercent))
    start.place(relx=0.6,rely=0.2,anchor=CENTER)

if __name__ == '__main__':
    App = Tk()
    inputpercent = StringVar()
    App.title("Text Summarizer")
    App.geometry('1300x800')
    App['background'] = 'cyan'
    filename=''
    percent=50
    choose = Button(App, text='Choose a pdf file', command= select_file)
    choose.place(relx=0.5, rely=0.1, anchor=CENTER)
    App.mainloop()