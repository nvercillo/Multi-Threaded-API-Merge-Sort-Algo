import time
import json
import os 
import sys
sys.path.insert(0, "..")  # import parent folder

from utils import Utils
import requests
from threading import Thread, Lock


if "SOURCE_URL" in os.environ:
    SOURCE_URL = os.environ["SOURCE_URL"] 
else:
    print("ERROR: MAKE SURE .env FILE EXISTS AND IS PROPERLY")
    exit()

MAX_THREADS = 2  # preformance plateaus then suffers after a crticial number of threads

class PostController:

    
    class MutableInt:
        def __init__(self, val):
            self.value = val
            self.mutex = Lock()

            

    def find_relevant_posts(self, request):
        
        if "tags" not in request or len(request['tags']) == 0:
            response = {
                "error" : "Tags parameter is required"
            }

            status = 400

            return response, status
    
        sortBy = "id" # default sort value
        if "sortBy" in request:     
            if request['sortBy'] not in ['id', 'reads', 'likes', 'popularity']:

                response = {
                    "error": "sortBy parameter is invalid"
                }

                status = 400

                return response, status
            sortBy = request['sortBy']
            
        direction = "asc"
        if "direction" in request:
            if request["direction"] not in ['asc', 'desc']:

                response = {
                    "error": "direction parameter is invalid" 
                }

                status = 400

                return response, status
            
            direction = request['direction']

        
        tags = request['tags'].split(",")

        n = len(tags)

        ''' NOTE:   Data does not need to be protected b/c the no two threads will 
                    ever have the same index at the same time 
        '''
        data =[[]] * n  # will contain the sorted subarrays calcualated by each thread
    

        lock_protected_thread_count = self.MutableInt(0) #  a mutable int is used b/c classes are mutable in python 

        thread_pool = []
        for _ in range(min(n, MAX_THREADS)):
            thread = Thread(target=self.get_tag_info_and_sort, args=(data, lock_protected_thread_count, tags, sortBy))
            thread_pool.append(thread)
            thread.start()

        for thread in thread_pool:
            thread.join()



        ''' Merge K Sorted Arrays '''
        sorted_array =  Utils.MergeKLists().merge_k_lists(data, sortBy)  
        
        ''' Remove Dulpicates'''
        sorted_array = Utils.remove_duplicates(sorted_array)

        if direction == "desc":
            sorted_array = Utils.reverse_list_of_dicts(sorted_array)

        return {"posts": sorted_array}, 200
        


    def get_tag_info_and_sort(self, data, lock_protected_thread_count, tags, sortBy):
        leave_fn = False
        while True:
            
            lock_protected_thread_count.mutex.acquire()
            if lock_protected_thread_count.value == len(tags):
                leave_fn = True 
            else:
                index = lock_protected_thread_count.value
                lock_protected_thread_count.value +=1 
            lock_protected_thread_count.mutex.release()
            
            if leave_fn:
                break
            
            
            res = requests.get(url=f"{SOURCE_URL}/?tag={tags[index]}")


            # occasionally requests fail, retry until a good request is achieved
            max_retries = 10
            while res.status_code != 200 and max_retries:

                time.sleep(500)
                res = requests.get(url=f"{SOURCE_URL}/?tag={tags[index]}")

                max_retries -=1


            res_data = json.loads(res.text)
            posts = res_data['posts']


            posts.sort(key = lambda d: d[sortBy])

            data[index] = posts


# response, status= PostController().find_relevant_posts(
#     {
#         "tags" : "tech,health,science,design,history,culture",
#         "direction" : "desc"
#     }
# )

# print(response, status)