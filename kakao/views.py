# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
import datetime
from apiclient.discovery import build
import numpy as np
import gensim

from gensim.models.keyedvectors import KeyedVectors
from sklearn.preprocessing import normalize
from gensim.models import FastText
import pickle

#cache
model_cache_key = 'model_cache' 
# this key is used to `set` and `get` 
# your trained model from the cache

model = cache.get(model_cache_key) # get model from cache

url_cache_key = 'url_cache'

url_vec= cache.get(url_cache_key)


if model is None:
    # your model isn't in the cache
    # so `set` it
    #model = KeyedVectors.load_word2vec_format('/home/ubuntu/Django/kakao/vectors.bin', binary=True,limit=50000,datatype=np.float32)
    model = FastText.load('/home/ubuntu/Django/kakao/Fasttext') # load model
    cache.set(model_cache_key, model, None) # save in the cache
     # in above line, None is the timeout parameter. It means cache forever
    model.init_sims() 

if url_vec is None:
    url_vec=pickle.load(open( "/home/ubuntu/Django/kakao/url_vec.p", "rb" ))   
    cache.set(url_cache_key, url_vec, None)




#for inital state 
def keyboard(request):
        return JsonResponse({
        'type' : 'text'})


#answer 
@csrf_exempt
def answer(request):
    json_str = ((request.body).decode('utf-8'))
    return_json_str = json.loads(json_str)
    return_str = return_json_str['content']
    
    query=return_str.strip().lower().split()    
    
    query_vec=np.zeros((50))     
    
    #query_vec=model.wv.word_vec("asdf",use_norm=True) not working 
    
    for q in query:
        query_vec+=model.wv[q]
    
    query_vec=normalize(query_vec.reshape(1,-1))
    query_vec=np.squeeze(query_vec)
    
    max_url=""
    max_sim=0
    for k,v in url_vec.items():
        dot=v.dot(query_vec)
        if(max_sim<dot):
            max_url=k
            max_sim=dot 
    



    return JsonResponse({
        'message': {
		'text': max_url
	  	#'text': youtube_search(return_str,1)
        },
        'keyboard': {
            'type': 'text'
        }
    })

def youtube_search(q, max_results):
    youtube = build("youtube", "v3", developerKey= "AIzaSyBw1WcdJJC_YzCbv6jqfzCTc1ecaIemrNE")
    search_response = youtube.search().list(q=q, part="id,snippet",maxResults=max_results).execute()
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            return "https://www.youtube.com/watch?v="+search_result["id"]["videoId"]
# Create your views here.
