import json 
import pytest
import requests
import os
from utils import Utils
from dotenv import load_dotenv
from os.path import join, dirname
load_dotenv(join(dirname(__file__), '../.env'))

if "SOURCE_URL" in os.environ:
    SOURCE_URL = os.environ["SOURCE_URL"] 
else:
    print("ERROR: MAKE SURE .env FILE EXISTS AND IS PROPERLY")
    exit()

DEFAULT_URL = "http://127.0.0.1:5000"


class RequestingClass:
    @staticmethod
    def _assert_code(e_code, response):
        code = response.status_code
        msg = f"Got code {code}, expected {e_code}, response={response.json()}"
        assert code == e_code, msg


class TestApiFunctionality:

    def setup_class(self):
        # check whether local instance running
        try:
            requests.get(DEFAULT_URL)
        except:
            print("LOCAL INSTANCE NOT RUNNING ON PORT 5000!")
            pytest.exit("LOCAL INSTANCE NOT RUNNING ON PORT 5000!")
                
    class TestPing(RequestingClass):

        @pytest.mark.ping
        def test_basic_ping(self):        
            print("Running test_basic_ping")
            expected_status_code = 200
            response = requests.get(f"{DEFAULT_URL}/api/ping")
            self._assert_code(expected_status_code, response)
            print("PASSED test_basic_ping")


    class TestPost(RequestingClass):

        long_tags = "tech,health,science,design,history,culture"

        @pytest.mark.posts
        @pytest.mark.invalid
        def test_missing_tag(self):        
            print("Running test_missing_tag")
            expected_status_code = 400
            response = requests.get(f"{DEFAULT_URL}/api/posts")
            self._assert_code(expected_status_code, response)
            print("PASSED test_missing_tag")

        @pytest.mark.posts
        @pytest.mark.invalid
        def test_missing_tag2(self):        
            print("Running test_missing_tag2")
            expected_status_code = 400
            response = requests.get(f"{DEFAULT_URL}/api/posts?tags=&sortBy=id")
            self._assert_code(expected_status_code, response)
            print("PASSED test_missing_tag2")

        @pytest.mark.posts
        @pytest.mark.invalid
        def test_invalid_dir(self):        
            print("Running test_invalid_dir")
            expected_status_code = 400
            response = requests.get(f"{DEFAULT_URL}/api/posts?tags=tech&direction=sdfsdfsdfsd")
            self._assert_code(expected_status_code, response)
            print("PASSED test_invalid_dir")

        @pytest.mark.posts
        @pytest.mark.invalid
        def test_invalid_sort(self):        
            print("Running test_invalid_sort")
            expected_status_code = 400
            response = requests.get(f"{DEFAULT_URL}/api/posts?tags=tech&sortBy=ppp")
            self._assert_code(expected_status_code, response)
            print("PASSED test_invalid_dir")

        

        
        @pytest.mark.parametrize(
            "sortBy", 
            # ['likes', 'popularity']
            ['id', 'reads', 'likes', 'popularity']
        )

        @pytest.mark.parametrize(
            "direction", 
            [ 'asc', 'desc']
        )
        @pytest.mark.posts
        @pytest.mark.invalid
        def test_valid_sort(self, sortBy, direction):        
            
            print("Running test_valid_sort")
            expected_status_code = 200

            uri = f"{DEFAULT_URL}/api/posts?tags={self.long_tags}&sortBy={sortBy}&direction={direction}"


            response = requests.get(uri)
            
            res_data = json.loads(response.text)

            gotten_posts = res_data['posts']
            expected_posts = self.get_posts_data(sortBy, reverse=direction  == "desc")
            print("\nGOT " , [d[sortBy] for d in gotten_posts])

            print(f"Got {len(gotten_posts)}, Expected {len(expected_posts)}")

            # check for sorted order 
            if direction == "asc":
                assert all(gotten_posts[i][sortBy] <= gotten_posts[i+1][sortBy] for i in range(len(gotten_posts)-1))
            else:
                assert all(gotten_posts[i][sortBy] >= gotten_posts[i+1][sortBy] for i in range(len(gotten_posts)-1))

            self._assert_code(expected_status_code, response)
            print("PASSED test_valid_sort")

        
        def get_posts_data(self, sortBy, reverse=False):
            tags = self.long_tags.split(",")
            
            data = []

            for t in tags:
                res = requests.get(url=f"{SOURCE_URL}/?tag={t}")

                res_data = json.loads(res.text)
                posts = res_data['posts']

                data.extend(posts)

            
            data.sort( key = lambda d: d[sortBy], reverse=reverse)
            data = Utils.remove_duplicates(data)
            print("EXP" ,[d[sortBy] for d in data])

            return data




