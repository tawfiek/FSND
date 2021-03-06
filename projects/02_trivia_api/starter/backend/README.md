# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/categories'
GET '/questions'
POST '/questions'
DELETE '/questions/<int:question_id>'
POST '/quizzes'


GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a categories, that contains a object of id: category_string key:value pairs, and success, a boolean that discribe the status of the call

{
    "success": true,
    "categories": {
        ...
        "1": "art",
        ...
    }
}


GET '/questions'

- Fetches an array of questions and ictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: page => It is an integer number of page you want to get. 
- Returns: An object with a categories, that contains a object of id: category_string key:value pairs, success, a boolean that discribe the status of the call and total_questions, that contain the number of returned questions, questions, an array of questions , current_category, that is 1 by defualt


{
    "categories": {1: "Science", 2: "Art", 3: "Geography", 4: "History", 5: "Entertainment", 6: "Sports"}
    "current_category": 1
    "questions": [
        ...
        {answer: "Apollo 13", category: 5, difficulty: 4, id: 2}
        ...
    ]
    "success": true
    "total_questions": 19
}


POST '/questions'

- Adding a new question
- Request Arguments: None
- Request Body: { 
    "answer": "adsfasd"
    "category": "4"
    "difficulty": 1
    "question": "asdasd"
}
- Returns: the new questions that has been added successfully
{ 
    "id": 26,
    "answer": "adsfasd"
    "category": "4"
    "difficulty": 1
    "question": "asdasd"
}


DELETE '/questions/<int:question_id>'

- Deleting the question that given the the id for 
- Request Arguments: question_id => the id of thae question needs to be deleted
- Returns: An object that contains a single key success, a boolean that discribe the status of the call

{"success": true} 


POST '/quizzes'

- Get the next question in the quiz
- Request Arguments: None
- Request Body: {
    "previous_questions": [... 17, ...]
    "0": 17
    "quiz_category": {type: "Art", id: "2"}
    "id": "2"
    "type": "Art"
}
- Returns: An object that contains forceEnd, a boolean that indecate the end of the quiz and question 
{
    forceEnd: false
    question: {
        "answer": "asdasd"
        "category": 2
        "difficulty": 3
        "id": 25
        "question": "asdasd"
    }
}


```

##Error Handling 

Errors are returned as JSON object in the dollowing format: 

```json
 {
      "success": false,
      "message": "Resources not found",
      "error": 404
 }
```

The API will return three error types when request fial:

* 400: Bad Request
* 422: Unprocessable entity
* 404: Resources not found


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

        
   
