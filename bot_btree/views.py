from django.shortcuts import render

# Create your views here.
from twilio.twiml.messaging_response import MessagingResponse
from django.views.decorators.csrf import csrf_exempt

#librerías para el programa
from django.http import HttpResponse
import emoji
import requests
import random
import datetime
import json
"""
https://dev.to/zeyu2001/i-built-a-python-whatsapp-bot-to-keep-me-sane-during-quarantine-nph
https://apify.com/store?search=cat
"""

@csrf_exempt
def index(request):
    if request.method == 'POST':
        # retrieve incoming message from POST request in lowercase
        incoming_msg = request.POST['Body'].lower()
        # create Twilio XML response
        resp = MessagingResponse()
        msg = resp.message()

        responded = False
        print('Thanks God!!!')

        if incoming_msg == 'hello':
            #response = "*Hi! I am the Quarantine Bot*"
            
            response = emoji.emojize("""
*Hola soy BTree Bot* :wave:
A tu servicio! :wink:
Envíame estos comandos:
:black_small_square: *'frase':* Frase inspiradora in English :rocket:
:black_small_square: *'perro':* Foto de tu amigo fiel :dog:
:black_small_square: *'gato':* Foto de un felino :cat:
:black_small_square: *'noticias':* Noticias in English :newspaper:
:black_small_square: *'servicios':* Servicios BTree :computer:
                """, use_aliases=True)

            msg.body(response)
            responded = True

        elif incoming_msg == 'frase':
            #return a quote
            print('*********Entro a quote*********')
            r = requests.get('https://api.quotable.io/random')

            if r.status_code == 200:
                data = r.json()
                quote = f'{data["content"]} ({data["author"]})' 
            else:
                quote = 'I could not receive a quote at this moment.'

            msg.body(quote)
            responded = True

        elif incoming_msg == 'gato':
            #return a cat picture
            msg.media('https://cataas.com/cat')
            responded = True

        elif incoming_msg == 'perro':
            #return a dog picture
            r = requests.get('https://dog.ceo/api/breeds/image/random')                              
            data = r.json()
            msg.media(data['message'])
            responded = True

        elif incoming_msg == 'servicios':
            data = {'message': 'Análisis de datos\nCursos Python/PHP/SQL\nFacturación electrónica\nAsesoría Moodle'}
            #data['message'] = '{jajaja}'
            msg.body(data['message'])
            responded = True
        

        elif incoming_msg == 'noticias':
            r = requests.get('https://newsapi.org/v2/top-headlines?sources=bbc-news,the-washington-post,the-wall-street-journal,cnn,fox-news,cnbc,abc-news,business-insider-uk,google-news-uk,independent&apiKey=3ff5909978da49b68997fd2a1e21fae8')

            if r.status_code == 200:
                data = r.json()
                articles = data['articles'][:5]
                result = ''

                for article in articles:
                    title = article['title']
                    url = article['url']
                    if 'Z' in article['publishedAt']:
                        published_at = datetime.datetime.strptime(article['publishedAt'][:19], "%Y-%m-%dT%H:%M:%S")
                    else:
                        published_at = datetime.datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%S%z")

                    result += """
*{}*
Read more: {}
_Published at {:}/{:}/{:} {:}:{}:{} UTC_
""".format(
    title,
    url,
    published_at.day,
    published_at.month,
    published_at.year,
    published_at.hour,
    published_at.minute,
    published_at.second
    )
            else:
                result = 'I can not fetch news at this time.  Sorry!'
            msg.body(result)
            responded = True

        elif incoming_msg.startswith('servicios'):
            #run task to aggregate covid news
            requests.post('https://api.apify.com/v2/actor-tasks/5MjRnMQJNMQ8TybLD/run-sync?token=qTt3H59g5qoWzesLWXeBKhsXu&ui=1')

            #get the last run dataset items
            r = requests.get('https://api.apify.com/v2/actor-tasks/5MjRnMQJNMQ8TybLD/runs/last/dataset/items?token=qTt3H59g5qoWzesLWXeBKhsXu')
            if r.status_code == 200:
                data = r.json()
                country = incoming_msg.replace('statistics', '')
                country = country.strip()
                country_data = list(filter(lambda x: x['country'].lower().startswith(country), data))
                if(country_data):
                    result = ''
                    for i in range(len(country_data)):
                        data_dict = country_data[i]
                        last_updated = datetime.datetime.strptime(data_dict.get('lastUpdateApify', None), "%Y-%m-%d%H:%M:%S.%fZ")
                        result += """
*Statistics for country {}*
Infected: {}
Tested: {}
Recovered: {}
Deceased: {}
Last updated: {:02}/{:02}/{:02} {:02}:{02}:{03} UTC
""".format(
    data_dict['country'],
    data_dict.get('infected', 'NA'),
    data_dict.get('tested', 'NA'),
    data_dict.get('recovered', 'NA'),
    data_dict.get('deceased', 'NA'),
    last_updated.day,
    last_updated.month,
    last_updated.year,
    last_updated.hour,
    last_updated.minute,
    last_updated.second
    )
                else:
                    result = "Country data not found"
            else:
                result = "I can not retrieve statistics at this time"        
            msg.body(result)    
            responded = True

        elif incoming_msg.startswith('meme'):
            r = requests.get('https://www.reddit.com/r/memes/top.json?limit=20?t=day', headers = {'User-agent': 'your bot 0.1'})
            if r.status_code == 200:
                data = r.json()
                memes = data['data']['children']
                random_meme = random.choice(memes)
                meme_data = random_meme['data']
                title = meme_data['title']
                image = meme_data['url']
                msg.body(title)
                msg.media(image)
            else:
                msg.body('Sorry, I can not retrieve memes now!')

            responded = True    

        if not responded:
            msg.body("Lo siento, no entiendo.  Envía hello para el menú.")


        return HttpResponse(str(resp))