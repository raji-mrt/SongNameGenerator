""" A simple dictionary for adverbs """
import random
import boto3
from boto3.dynamodb.conditions import Key
import singularize
import requests

dynamodb = boto3.resource('dynamodb')
table_blacklisted = dynamodb.Table('blacklisted_words')
table_datamuse = dynamodb.Table('datamuse_cache')


def validate_word(word):
    if " " in word:
        return False
    response = table_blacklisted.query(
        KeyConditionExpression=Key('word').eq(word)
    )
    if response['Count'] > 0:
        print('---This word is black listed')
        return False
    return True


def read_from_datamuse(word):
    singular_word = singularize.singularize(word)
    output_word = ''
    print('===Searching the db for  =' + singular_word)
    response = table_datamuse.query(
        KeyConditionExpression=Key('word').eq(word)
    )
    if response['Count'] > 0:
        print(response)
        while True:
            output_word = random.choice(response['Items'][0]['datamuse'][:10])['word']
            if validate_word(output_word):
                break
    else:
        print('===Database cache does not have =' + singular_word)

    print('===Database fetched output =' + output_word)

    if not output_word:
        # This means that the word is not available in database
        response = requests.get('https://api.datamuse.com/words?ml=' + singular_word)
        if response.status_code != 200:
            print("===datamuse is rejecting the request : " + response.status_code)
        else:
            formatted = response.json()
            if len(formatted) > 0:
                for element in formatted:
                    element.pop('score', None)
                    element.pop('tags', None)
                # Add the data to database and return a similar value
                table_datamuse.put_item(Item={'word': singular_word,
                                     'datamuse': formatted})
                while True:
                    output_word = random.choice(formatted[:10])['word']
                    if validate_word(output_word):
                        break

    return output_word


def get_close_word(word):
    lowercase_word = word.lower()
    verb_to_be = set(['am', 'are', 'is', 'was', 'were', 'been', 'being'])
    preposition = set(['above', 'after', 'afterwards', 'against', 'among', 'as', 'at', 'in', 'on', 'below', 'beneath',
                       'beyond', 'by', 'during', 'for', 'for', 'from', 'into', 'near', 'of', 'on', 'onto', 'over', 'to',
                       'under', 'until',  'with', 'within', 'without'])
    pronouns = (['all', 'another', 'any', 'anybody', 'anyone', 'anything', 'as', 'aught', 'both', 'each', 'each other',
                  'either', 'enough', 'everybody', 'everyone', 'everything', 'few', 'he', 'her', 'hers', 'herself',
                  'him', 'himself', 'his', 'i', 'idem', 'it', 'its', 'itself', 'many', 'me', 'mine', 'most', 'my',
                  'myself', 'naught', 'neither', 'no one', 'nobody', 'none', 'nothing','nought', 'one', 'one another',
                  'other', 'others', 'ought', 'our', 'ours', 'ourself', 'ourselves', 'several', 'she', 'some',
                  'somebody', 'someone', 'something', 'somewhat', 'such', 'suchlike', 'that', 'thee', 'their',
                  'theirs', 'theirself', 'theirselves', 'them', 'themself', 'themselves', 'there', 'these', 'they',
                  'thine', 'this', 'those', 'thou', 'thy', 'thyself', 'us', 'we', 'what', 'whatever', 'whatnot',
                  'whatsoever', 'whence', 'where', 'whereby', 'wherefrom', 'wherein', 'whereinto', 'whereof', 'whereon',
                  'wherever', 'wheresoever', 'whereto', 'whereunto', 'wherewith', 'wherewithal', 'whether', 'which',
                  'whichever', 'whichsoever', 'who', 'whoever', 'whom', 'whomever', 'whomso', 'whomsoever', 'whose',
                  'whosever', 'whosesoever', 'whoso', 'whosoever', 'ye', 'yon', 'yonder', 'you', 'your', 'yours',
                  'yourself', 'yourselves'])

    if lowercase_word in verb_to_be:
        return random.sample(verb_to_be, 1).pop().capitalize()
    if lowercase_word in preposition:
        return random.sample(preposition, 1).pop().capitalize()
    if lowercase_word in pronouns:
        return random.sample(pronouns, 1).pop().capitalize()
    else:
        print('===Not found in in memory cache  = ' + lowercase_word)
        return read_from_datamuse(lowercase_word).capitalize()
