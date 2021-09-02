from flask import Flask

class Utils: 

    @staticmethod
    def reverse_list_of_dicts(arr):

        i =0 
        while i < len(arr) //2:
            t = arr[i]
            arr[i] = arr[len(arr)-1 -i]
            arr[len(arr)-1 -i] = t

            i+=1
        
        return arr

    @staticmethod
    def remove_duplicates(arr, primary_key="id"):
        
        new_arr = [] 
        unique = set({})

        for e in arr:
            if e[primary_key] not in unique:
                new_arr.append(e)
                unique.add(e[primary_key])
        
        return new_arr



        
    class Config:

        def get_app_with_db_configured(self):
            app = Flask(__name__)

            self.config_app(app)
            return app

        def config_app(self, app):
            config = {
                "DEBUG": True,          # some Flask specific configs
                "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
                "CACHE_DEFAULT_TIMEOUT": 300
            }            

            app.config.from_mapping(config)
            

    class MergeKLists:
        def merge_k_lists(self, lists, sort_key):
            interval = 1
            while interval < len(lists):
                i = 0 
                while i < len(lists)-interval:
                    lists[i] = self.merge_two_lists(lists[i], lists[i + interval], sort_key)
                    
                    i += interval
                interval *= 2
                
            return lists[0] if len(lists) != 0 else None
        

        def merge_two_lists(self, l1, l2, primary_sort_key, secondary_sort_key=None):

            
            new_arr = []

            l1ind = 0 
            l2ind = 0 
            
            while l1ind < len(l1) and l2ind < len(l2): 
                
                if (l1[l1ind][primary_sort_key] <= l2[l2ind][primary_sort_key]) or (secondary_sort_key  and l1[l1ind][secondary_sort_key] <= l2[l2ind][secondary_sort_key]):
                    new_arr.append(l1[l1ind])
                    l1ind +=1 
                else:

                    new_arr.append(l2[l2ind])
                    l2ind +=1

            if l1ind >= len(l1):
                new_arr += l2[l2ind:]
            else:
                new_arr += l1[l1ind:]

            return new_arr


