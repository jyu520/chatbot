#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2016
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Ported to Java by Raghav Gupta (@rgupta93) and Jennifer Lu (@jenylu)
######################################################################
import csv
import math
import re
import numpy as np
from numpy import linalg as LA
import string
import random

from movielens import ratings
from random import randint
from PorterStemmer import PorterStemmer

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.p = PorterStemmer()
      self.read_data()
      self.user_vec = {}
      self.english_articles = ['the', 'a', 'an']
      self.strong_pos_sentiment = ['love', 'favorit', 'amaz']      
      self.strong_neg_sentiment = ['hate']
      self.intensifier_sentiment = ["veri", "realli", "extrem"]
      self.negation_words = ['not', 'no', 'never']
      self.responding_to_possibilities = False
      self.possible_indices = []
      self.sentiment_of_possible = ''
      self.mention_movie = ""
      self.mention_move_sentiment = ""

      self.responses = {}
      self.responses['no_title_starter'] = \
      ["Sorry, I don't understand..film is my one area of expertise!",
      "Hmm..ok. Let's get back to movies!",
      "Okay, got it. Let's talk about movies.",
      "Interesting... Let's talk about movies.",
      "I see what you're saying... Let's get back to movies!",
      "Ah, I see... Hey, let's talk about movies!"]
      
      self.responses['multiple_titles_starter'] = \
      ["Whoa! Easy there champ. I can only handle one movie at a time..let's try again.",
      "Hmm...my head hurts. Please only ask me about one movie at a time!",
      "You have a lot of opinions, don't you? Unfortunately I can only process one movie at a time.",
      "Whoa! Slow down there speedracer. I can only handle one movie at a time.. let's try again.",
      "Hold your horses! I can only handle one movie at a time.. let's try again.",
      "Ruh-roh, I can only handle one movie at a time.. let's try again."]
      
      self.responses['title_not_in_db_starter'] = \
      ["Unfortunately I haven't heard of \"%s\".",
      "I'm racking my brain but I don't think I know anything about \"%s\"..sorry.",
      "Hmm..I'm not sure I've seen \"%s\".",
      "Don't think I've heard of \"%s\" before.",
      "Haven't heard of \"%s\".",
      "I don't believe we have any information on \"%s\".",
      "I can't seem to find \"%s\" in my movie database.",
      "I don't believe I know the movie \"%s\".",
      "Never heard of \"%s\"."]

      self.responses['liked_movie_starter'] = \
      ["Nice! I liked \"%s\" too.",
      "Interesting, I wasn't a huge fan of \"%s\", but to each their own, right?",
      "\"%s\" is one of my favorites! Great minds think alike.",
      "\"%s\" is my all time favorite! You really have good taste.",
      "\"%s\" is a classic!",
      "Oh, I hated \"%s\"... guess we'll have to agree to disagree, right?",
      "Errrhm, \"%s\" is not my favorite but I am glad you liked it!.", 
      "Cool! I thought \"%s\" was great too.",
      "Agreed. I would definitely watch \"%s\" again.",
      "Wicked! I loved \"%s\" too."]

      self.responses['disliked_movie_starter'] = \
      ["Agreed, I wasn't a huge fan of \"%s\".",
      "Huh - I really liked \"%s\". I guess we can't agree on everything!",
      "Yeah, I didn't think \"%s\" was anything to write home about either.",
      "Next! I didn't like \"%s\" either.", "Ya seriously, I found \"%s\" quite bad as well.",
      "What?! I loved \"%s\", guess we'll have to agree to disagree, right?",
      "Oh my heart! I personally adored \"%s\", but to each their own, right?",
      "Couldn't have said it better myself, \"%s\" was not good.",
      "Zzz... I am also not a fan of \"%s\".",
      "Ditto! \"%s\" sucked."]


      #dont prompt again
      self.responses['no_sentiment_starter'] = \
      ["Okay..so you saw \"%s\". Tell me how you felt about it!",
       "Cool, I just saw \"%s\"! Tell me more about how it made you feel.",
       "Alright, so you saw \"%s\". Tell me more about how it made you feel.",
       "Oh, I just watched \"%s\". Tell me more about how it made you feel.",
       "Nice, so you saw \"%s\". Tell me more about how it made you feel."]

       #don't prompt agian
      self.responses['equal_sentiment_starter'] = \
      ["I'm not sure whether you liked or disliked \"%s\". Can you tell me more?",
      "Hmm..I can't tell how you feel about \"%s\". What were your feelings about it?",
      "I see.. I can't quite tell how you feel about \"%s\". Can you tell me more?",
      "Ah, I'm not sure if you like \"%s\" or not. What were your feelings about it?",
      "Unsure if you liked or disliked \"%s\". Can you tell me how you feel about it?"]

      self.responses['recommendation_starter'] = \
      ["\nThat was a solid list of movies!\nBased on your tastes, I think you should watch \"%s\".",
      "\nThanks for all your input! I'd like to give you a recommendation.\nI suggest you watch \"%s\".",
      "\nSweet! That's all I needed to hear.\nBased on your tastes, I suggest you watch \"%s\".",
      "\nAwesome! That's a good enough list for me to give you a recommendation.\nI think you'd like \"%s\".",
      "\nAlrighty, based off those movies, I'd like to give you a recommendation\n I suggest you watch \"%s\"."]

      self.responses['play_again'] = \
      ["\nIf you'd like another recommendation, tell me about another movie you've seen (or enter :quit if you're done!)"]

      self.responses['prompt_again'] = \
      ["Tell me about a movie that you have seen.",
       "What have you seen recently, and how did it make you feel?",
       "Have you seen anything recently you feel strongly about?",
       "Tell me about another movie.",
       "Tell me about some other movie you've seen recently!",
       "Can you tell me about another movie?",
       "What other movies do you have feelings about?",
       "What other movie do you feel strongly about?",
       "What is another movie you've seen?",
       "Could you tell me about another movie you feel strongly about?",
       "What is another movie you feel strongly about?"]
      self.first_process = True


    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      greeting_message = 'Hello! I make movie recommendations. Tell me about a movie you have seen.'
      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      goodbye_message = 'Thanks for playing. Have a nice day!'
      return goodbye_message

    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def process(self, input):

      if self.first_process:
        self.first_process = False
        if self.is_turbo:
          self.mean_center()
        else:
          self.binarize()
        for vec in self.ratings:
          vec = self.normalize_vec(vec)

      response = ""
      sentiment = ""
      dbIndex = -1
      user_title = ""

      if self.is_turbo and len(input.split()) > 2:
        split_input = input.split()
        first_two_words = split_input[0:2]
        first_two_words = " ".join(first_two_words).lower()
        if first_two_words == "can you" or first_two_words == "what is":
          rest = split_input[2:]
          last_word = rest[-1]
          #print last_word[-1]
          #print string.punctuation
          if last_word[-1] in string.punctuation:
            rest[-1] = last_word[:-1]

          for i in xrange(0, len(rest)):
            if rest[i] == "me":
              rest[i] = "you"
            if rest[i] == "my":
              rest[i] = "your"
            if rest[i] == "this":
              rest[i] = "that"

          
          rest = " ".join(rest)
          
          if first_two_words == "can you":
            response = "Sorry, I can't %s. Let's get back to movies!" % rest
            return response
          elif first_two_words == "what is":
            response = "Hmm..I don't know what %s is. Let's talk about movies." % rest
          return response

      multiple_titles = False
      opposing_sentiment = False
      retrieved_title_2 = ""


      if self.responding_to_possibilities:
        input_without_title = ""
        dbIndex = self.possible_indices[int(input)-1]
        user_title = self.titles[dbIndex][0]
        sentiment = self.sentiment_of_possible

      else:
        
        #find title in input
        user_title = self.find_input_title(input)
        if user_title == "":
          if self.is_turbo:
            if self.mention_movie != "" and ("that" in input.lower() or "it" in input.lower()):
              user_title = self.mention_movie
              #print 'Found previous movie: %s' % user_title
            else:
              #print "No title found in input. Sad!"
              response = self.respond_to_user('no_title_starter', '')
              return response
          else:
              #print "No title found in input. Sad!"
              response = self.respond_to_user('no_title_starter', '')
              return response
        elif user_title == "multiple":
            if self.is_turbo:
              titles = self.find_mult_title(input)
              user_title = titles[0]
              user_title2 = titles[1]
              multiple_titles = True
              indices_title_2 = self.find_database_title(user_title2)
              if len(indices_title_2) == 0:
                response = self.respond_to_user('title_not_in_db_starter', user_title2)
                return response
              elif len(indices_title_2) > 1:
                response = "I found too many results for \"%s\". I can't find multiple movies unless you give me their exact names ):"
                return response
              else:
                dbIndex2 = indices_title_2[0]
                retrieved_title_2 = self.titles[dbIndex2]
                for i in range(len(input.split())):
                  word = input.split()[i]
                  if word == 'but' or word == 'however':
                    opposing_sentiment = True
                    splitIndex = i
                    input1 = " ".join(input.split()[:splitIndex])
                    input2 = " ".join(input.split()[splitIndex:])

            else:
              response = self.respond_to_user('multiple_titles_starter', '')
              return response
        else:
          if self.is_turbo == True:
            self.mention_movie = user_title
            #print self.mention_movie
            #print "Title found in input: %s" % user_title
          #else:
            #pass
           # print "Title found in input: %s" % user_title
            
        #find title in database
        indices = self.find_database_title(user_title)
        dbIndex = -1
        possibleTitles = []
        #print 'Database indices: %s' % str(indices)
        if len(indices) == 0:
          #print "Title not found in database. Sad!"
          response = self.respond_to_user('title_not_in_db_starter', user_title)
          return response
        if len(indices) == 1:
          dbIndex = indices[0]
          retrieved_title = self.titles[dbIndex]
          #print "Title found in database: %s" % retrieved_title
        elif self.is_turbo:
          self.possible_indices = indices
          num = 0
          for index in indices:
            num += 1
            retrieved_title = self.titles[index][0]
            #print "Title found in database: %s" % retrieved_title
            possibleTitles.append(("(%s) " + retrieved_title) % str(num))
          self.responding_to_possibilities = True
          
        



         #input without title
        input_without_title = self.input_title_remove(input, user_title)
        #print "Input without title: %s" % input_without_title 
        
        #stem input
        stemmedInput = self.stem_input(input_without_title)
        #print "Stemmed input: %s" % stemmedInput

        #extract sentiment
        sentiment = self.extract_sentiment(stemmedInput)
        #print "Sentiment extracted from input: %s" % sentiment

        if self.responding_to_possibilities:
          self.sentiment_of_possible = sentiment
          return self.respond_with_title_possibilities(possibleTitles)

      if self.responding_to_possibilities:  
          self.sentiment_of_possible = ''
          self.possible_indices = []
          self.responding_to_possibilities = False

      if sentiment == "pos":
        self.user_vec[dbIndex] = 1
        if multiple_titles:
          if opposing_sentiment:
            self.user_vec[dbIndex2] = -1
            response = self.respond_to_user_multiple_titles('pos', user_title, user_title2, True)
          else:
            self.user_vec[dbIndex2] = 1
            response = self.respond_to_user_multiple_titles('pos', user_title, user_title2, False)
        else:
          response = self.respond_to_user('liked_movie_starter', user_title)
      elif sentiment == "neg":
        self.user_vec[dbIndex] = -1
        if multiple_titles:
          if opposing_sentiment:
            response = self.respond_to_user_multiple_titles('neg', user_title, user_title2, True)
            self.user_vec[dbIndex2] = 1
          else:
            response = self.respond_to_user_multiple_titles('neg', user_title, user_title2, False)
            self.user_vec[dbIndex2] = -1

        else:
          response = self.respond_to_user('disliked_movie_starter', user_title)
        
      elif sentiment == "none":
        if input_without_title == "":
          response = "I'm unsure how you felt about \"%s\". Can you tell me more?" % user_title
          return response
        if len(self.user_vec) > 0 and self.mention_movie != "":
          previous_sentiment = self.mention_move_sentiment
          if 'not' in input.lower():
            if previous_sentiment == 'pos':
              previous_sentiment = 'neg'
              self.user_vec[dbIndex] = -1
              response = self.respond_to_user('disliked_movie_starter', user_title)
            else:
              #est this - what if prev sentiment none or unclear?
              previous_sentiment = 'pos'
              self.user_vec[dbIndex] = 1
              response = self.respond_to_user('liked_movie_starter', user_title)
          elif 'and' in input.lower():
            if previous_sentiment == 'pos':
              self.user_vec[dbIndex] = 1
              response = self.respond_to_user('liked_movie_starter', user_title)
            else:
              self.user_vec[dbIndex] = -1
              response = self.respond_to_user('disliked_movie_starter', user_title)
          else:
            response = "I'm unsure how you felt about \"%s\". Can you tell me more?" % user_title
            return response
          sentiment = previous_sentiment
        else:
          response = self.respond_to_user('no_sentiment_starter', user_title)
      else:
        response = self.respond_to_user('equal_sentiment_starter', user_title)
        return response     
      
      print self.user_vec
      self.mention_move_sentiment = sentiment


      #if we reach here, user displayed sentiment for valid movie choice
      #either we recommend or prompt again
      if len(self.user_vec) > 4:
        recommended_title = self.recommend(self.user_vec)
        response += self.respond_to_user('recommendation_starter', recommended_title)
        self.user_vec = {}
      else:
        response += ' ' + self.respond_to_user('prompt_again', '')

      return response


    def find_mult_title(self, input):
      title = []
      match = re.findall("\"(.*?)\"", input)
      if len(match) > 0:
        for i in range(len(match)):
          title.append(str(match[i]))
      if len(title) < 1:
        title.append("")
      return title

    def respond_with_title_possibilities(self, possibleTitles):
      response = "Which of these movies are you talking about? [Respond with corresponding number].\n"
      for title in possibleTitles:
        response += title + "\n"
      return response


    def respond_to_user(self, status, user_title):
      if status == 'no_title_starter' or status == 'multiple_titles_starter':
        return self.choose_random(self.responses[status]) + ' ' + self.choose_random(self.responses['prompt_again'])

      if status == 'title_not_in_db_starter':
        return (self.choose_random(self.responses[status]) % user_title) + ' ' + self.choose_random(self.responses['prompt_again'])

      if status == 'liked_movie_starter' or status == 'disliked_movie_starter':
        return (self.choose_random(self.responses[status])) % user_title

      elif status == 'no_sentiment_starter' or status == 'equal_sentiment_starter':
        return (self.choose_random(self.responses[status])) % user_title
      
      elif status == 'recommendation_starter':
        return (self.choose_random(self.responses[status])) % user_title + self.choose_random(self.responses['play_again'])
      
      elif status == 'prompt_again':
        return self.choose_random(self.responses[status])
      
      return "Error - status of response not found"

    def respond_to_user_multiple_titles(self, status, user_title1, user_title2, opposing):
      if status == 'pos':
        if opposing:
          return ("Cool, you liked \"%s\" but not \"%s\"!" % (user_title1, user_title2))
        else:
          return ("Nice, you liked \"%s\" and \"%s\"!" % (user_title1, user_title2))
      elif status == 'neg':
        if opposing:
          return ("Cool, you didn't like \"%s\" but you liked \"%s\"!" % (user_title1, user_title2))
        else:
          return ("Okay, you didn't like \"%s\" or \"%s\"." % (user_title1, user_title2))


    def choose_random(self, list):
      return random.choice(list)

    def extract_sentiment(self, sentence):
      pos_sentiment_weight = 0
      neg_sentiment_weight = 0
      #for 
      title = False
      weightFlag = False
      negationFlag = False

      for word in sentence:
        if word in self.sentiment:
          #print "Sentiment word: %s" % word 
          sentiment = self.sentiment[word]
          sentiment_weight = 0

          if sentiment == 'pos':
            sentiment_weight += 1
            if word in self.strong_pos_sentiment:
              sentiment_weight += 1
            if weightFlag:
              sentiment_weight += 1
              weightFlag = False
            
            if negationFlag:
              neg_sentiment_weight += sentiment_weight
            else:
              pos_sentiment_weight += sentiment_weight
          else:
            sentiment_weight += 1
            if word in self.strong_neg_sentiment:
              sentiment_weight += 1
            if weightFlag:
              sentiment_weight += 1
              weightFlag = False

            if negationFlag:
              pos_sentiment_weight += sentiment_weight
            else:
              neg_sentiment_weight += sentiment_weight

        if word in self.intensifier_sentiment:
          weightFlag = True  
        if word in self.negation_words or 'n\'t' in word:
          negationFlag = True
        elif negationFlag:
          for punc in string.punctuation:
            if punc in word:
              #print 'negation turned off!'
              negationFlag = False
      
      #print '# Pos words ' + str(pos_sentiment_weight)
      #print '# Neg words ' + str(neg_sentiment_weight)

      if pos_sentiment_weight > neg_sentiment_weight:
        return 'pos'

      if pos_sentiment_weight == 0 and neg_sentiment_weight == 0:
        return 'none'

      if pos_sentiment_weight == neg_sentiment_weight:
        return 'unclear'

      return 'neg'

    def input_title_remove(self, input, user_title):
      input_without_title = user_title
      if self.title_contains_year(input_without_title):
        input_without_title = input_without_title.replace('(', '\(')
        input_without_title = input_without_title.replace(')', '\)')
      input_without_title = re.sub("\"%s\"" % input_without_title, '', input)
      return input_without_title

    def stem_input(self, input):
      stemmedInput = []
      for word in input.split():
        #necessary?
        word = word.strip(',.!?')
        stemmedInput.append(self.p.stem(word))
      return stemmedInput

    #find title in input
    def find_input_title(self, input):
      title = ""
      match = re.findall("\"(.*?)\"", input)
      if match:
        if len(match) > 1:
          title = 'multiple'
        else:
          title = match[0]

      return title

    def find_mult_title(self, input):
      title = []
      match = re.findall("\"(.*?)\"", input)
      if len(match) > 0:
        for i in range(len(match)):
          title.append(str(match[i]))
      if len(title) < 1:
        title.append("")
      return title


    #find inputed title in database and return index
    ###SEE PINNED POST ### should be able to find Matrix(1999)?
    #clean up 
    #implement creative
    def find_database_title(self, user_title):

      regex = ""
      user_title = user_title.lower()
      if self.is_turbo:
          #article in front
          regex1 = ""
          regex2 = ""
          regex3 = ""
          regex4 = ""

          if self.title_contains_year(user_title) and self.title_contains_article(user_title):
            user_title = user_title.replace('(', '\(')
            user_title = user_title.replace(')', '\)')
            user_title_split = user_title.split()
            first_word = user_title_split[0]
            year = user_title_split[-1]
            reduced_user_title = " ".join(user_title_split[1:-1])
            regex1 = "^(?:%s )?%s.*?(?: \(.+?\))*(?: %s)$" % (first_word, reduced_user_title, year)
            #article second
            regex2 = "^%s(?:, (?:%s))?(?: \(.+?\))*(?: %s)$" % (reduced_user_title, first_word, year)
            #title in paren
            regex3 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?(?:%s )?%s)\) )(?:\((?:.+?)\) )*(?:%s)$" % (first_word, reduced_user_title, year)
            regex4 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?%s(?:, (?:%s))?)\) )(?:\((?:.+?)\) )*(?:%s)$" % (first_word, reduced_user_title, year)

          elif self.title_contains_year(user_title):
            user_title = user_title.replace('(', '\(')
            user_title = user_title.replace(')', '\)')

            user_title_split = user_title.split()
            year = user_title_split[-1]
            reduced_user_title = " ".join(user_title_split[:-1])
            regex1 = "^(?:the |an |a )?%s.*?(?: \(.+?\))*(?: %s)$" % (reduced_user_title, year)
            #article second
            regex2 = "^%s(?:, (?:the|an|a))?(?: \(.+?\))*(?: %s)$" % (reduced_user_title, year)
            #title in paren
            regex3 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?(?:the |an |a )?%s)\) )(?:\((?:.+?)\) )*(?:%s)$" % (reduced_user_title, year)
            regex4 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?%s(?:, (?:the|an|a))?)\) )(?:\((?:.+?)\) )*(?:%s)$" % (reduced_user_title, year)

          elif self.title_contains_article(user_title):
            user_title = user_title.replace('(', '\(')
            user_title = user_title.replace(')', '\)')

            user_title_split = user_title.split()
            first_word = user_title_split[0]
            reduced_user_title = " ".join(user_title_split[1:])
            regex1 = "^(?:%s )?%s.*?(?: \(.+?\))*(?: \(\d{4}\))$" % (first_word, reduced_user_title)
            #article second
            regex2 = "^%s(?:, (?:%s))?(?: \(.+?\))*(?: \(\d{4}\))$" % (reduced_user_title, first_word)
            #title in paren
            regex3 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?(?:%s )?%s)\) )(?:\((?:.+?)\) )*\(\d{4}\)$" % (first_word, reduced_user_title)
            regex4 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?%s(?:, (?:%s))?)\) )(?:\((?:.+?)\) )*\(\d{4}\)$" % (reduced_user_title, first_word)

          else:
            user_title = user_title.replace('(', '\(')
            user_title = user_title.replace(')', '\)')
            regex1 = "^(?:the |an |a )?%s.*?(?: \(.+?\))*(?: \(\d{4}\))$" % user_title
            #article second
            regex2 = "^%s(?:, (?:the|an|a))?(?: \(.+?\))*(?: \(\d{4}\))$" % user_title
            #title in paren
            regex3 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?(?:the |an |a )?%s)\) )(?:\((?:.+?)\) )*\(\d{4}\)$" % user_title
            regex4 = "^.+?(?:\((?:.+?)\) )*(?:\((?:(?:a\.k\.a\. )?%s(?:, (?:the|an|a))?)\) )(?:\((?:.+?)\) )*\(\d{4}\)$" % user_title

          regex = regex1+"|"+regex2+"|"+regex3+"|"+regex4
      else:
        if self.title_contains_year(user_title):
          if self.title_contains_article(user_title):
            regex = self.regex_starter(user_title, True)
          else:
            regex = self.regex_starter(user_title, False)
        else:
          return []

      #print 'regex: ' + regex
      if self.is_turbo:
        possTitles = []
        for i in range (0, len(self.titles)): 
          currentTitle = self.titles[i][0]
          match = re.search(regex, currentTitle.lower())
          if match:
            possTitles.append(i)
        #print possTitles
        return possTitles

      else:
        for i in range (0, len(self.titles)): 
          currentTitle = self.titles[i][0]
          match = re.search(regex, currentTitle.lower())
          if match:
            return [i]
        return []

      
    def regex_starter(self, user_title, title_contains_article) :
      regex = ""
      if title_contains_article:
        first_word = user_title.split()[0]
        split_title = user_title.split('(', 1)
        reduced_user_title = split_title[0]
        split_reduced_user_title = reduced_user_title.split()
        reduced_user_title = " ".join(split_reduced_user_title[1:])
        rest = '(' + split_title[1]
        rest = rest.replace('(', '\(')
        rest = rest.replace(')', '\)')
        regex = "^%s %s %s$" % (first_word, reduced_user_title, rest)
        regex += "|^%s, %s %s$" % (reduced_user_title, first_word, rest)
      else:
        #add optional at beginning and end 
        split_title = user_title.split('(', 1)
        reduced_user_title = split_title[0]
        split_reduced_user_title = reduced_user_title.split()
        reduced_user_title = " ".join(split_reduced_user_title)
        rest = '(' + split_title[1]
        rest = rest.replace('(', '\(')
        rest = rest.replace(')', '\)')
        regex = "^(?:the |an |a )?%s %s$" % (reduced_user_title, rest)
        regex += "|^%s(?:, (?:the|an|a))? %s$" % (reduced_user_title, rest)
      return regex



    def title_contains_year(self, user_title):
      user_title_arr = user_title.split()
      match = re.search('\(\d{4}\)', user_title_arr[-1])
      if match:
        return True
      else:
        return False

    def title_contains_article(self, user_title):
      first_word = user_title.split()[0]
      if first_word in self.english_articles:
        return True
      return False

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j

      self.titles, self.ratings = ratings()
      reader = csv.reader(open('data/sentimentStemmed.txt', 'rb'))
      self.sentiment = dict(reader)

      

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      self.ratings[np.where(self.ratings >= 2.5)] = -2
      self.ratings[np.where(self.ratings >= 0.5)] = -1
      self.ratings[np.where(self.ratings == -2)] = 1

    def mean_center(self):
      self.ratings[np.where(self.ratings>0)] -= np.mean(self.ratings[np.where(self.ratings>0)])


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure
      return np.dot(u, v)
      
    def normalize_vec(self, u):
      norm = LA.norm(u)
      for i in xrange(0, len(u)):
        if u[i] != 0:
          u[i]=(u[i]/(norm))
      return u

    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot

      maxRecommend = 0
      maxRecommendIndex = 0
      for i in xrange(0, len(self.ratings)):
        if i in u:
          continue  
        sumRecommend = 0
        for userRatedMovie in u:
          sumRecommend += self.distance(self.ratings[i], self.ratings[userRatedMovie])*u[userRatedMovie]
        if sumRecommend > maxRecommend:
          maxRecommend = sumRecommend
          maxRecommendIndex = i
      
      recommended_title = self.titles[maxRecommendIndex][0]
      recommended_title = re.sub(' \(\d{4}\)', '', recommended_title)
      return recommended_title



    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Turn on turbo mode for special features such as:
        - finding alternate movie titles
        - non-binarized rating system
        - processing multiple movies at once
        - prompting user to specify ambiguous movies/series
        - understanding references to things said previously
        - fine-grained sentiment extraction
        - responds to arbitrary input and 'Can you..?' and 'What is..?' questions
        - note: features must be tested separately and 
          do not necessarily work if combined
      """
    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
