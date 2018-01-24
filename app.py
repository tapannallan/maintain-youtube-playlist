import pprint
import sys
import os
import os.path
import pickle
import simplejson as json
from apiclient.discovery import build

prev_list_file = 'output\prevlist.txt'
deleted_items_file = 'output\deleteditems.txt'

def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs

def get_all_playlist_items(client, **kwargs):
    
    kwargs = remove_empty_kwargs(**kwargs)

    all_items = {}    

    while(True):
        response = client.playlistItems().list(**kwargs).execute()
        for item in response['items']:
            id = item['id']
            title = item['snippet']['title']
            all_items[id] = title        
        if('nextPageToken' in response):
            kwargs['pageToken'] = response['nextPageToken']
        else:
            break    
    return all_items

if __name__ == '__main__':

    api_key = os.environ['GOOGLE_API_KEY']
    service = build('youtube', 'v3', developerKey=api_key)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    print('Fetching playlist')
    current_playlist_items = get_all_playlist_items(service,part='snippet,contentDetails',playlistId='PLwZYPD7MtnnzBFXr0izxrfgP37sopuAaF',maxResults=50)

    if os.path.isfile(prev_list_file):
        # Load Previous list
        prev_playlist_items = None
        with open(prev_list_file) as itemlistfile:
            content = itemlistfile.read()
            prev_playlist_items = json.loads(content)
        
        # Calculate differences
        print('Calculating difference')
        missing_keys = set(prev_playlist_items) - set(current_playlist_items)    

        if(len(missing_keys) > 0):        
            # Save to DeletedItems file
            print('Some Videos have been deleted')

            with open(deleted_items_file,'a') as deleteditems:
                for key in missing_keys:
                    deleteditems.write(key + ':' + prev_playlist_items[key] + '\n')

    #Pickle current list
    listjson = json.dumps(current_playlist_items,sort_keys=True, indent=4 * ' ')

    print('Replaced list file')
    with open(prev_list_file,'w') as itemlistfile:
        itemlistfile.write(listjson)

    print('Process Finished')