try:
    from flask_app import app, functions, bricklink_api
    import unittest
    import io
    import json
    import os
    import config
except Exception as e:
    print("Some modules are missing")


class FlaskTest(unittest.TestCase):

    def test_auth_file(self):
        self.assertTrue(os.path.isfile(config.BRICKLINK_AUTH_FILE), 'auth.json file not found in directory \"flask_app/bricklink_api\"')

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/")
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_home(self):
        tester = app.test_client(self)
        response = tester.get("/home")
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_home_loads(self):
        tester = app.test_client(self)
        response = tester.get("/home", content_type="html/text")
        self.assertTrue(b'Dashboard' in response.data)


    # def search_works(self):
    #     tester = app.test_client(self)
    #     response = tester.post("/search")

if __name__ == '__main__':
    unittest.main()