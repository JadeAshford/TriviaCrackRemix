import requests



def get_quiz_ids_by_user(user_id):
    API_ROOT = 'http://54.205.150.68:3000/'
    endpoint = API_ROOT + 'quiz?order=quiz_id.asc'



class Question:
    def __init__(self, question_text: str):
        self.question = question_text
        self.answers = []
    
    def add_answer(self, answer: str, correct: bool):
        self.answers.append((answer, correct))

    def __str__(self):
        to_return = f'Question: {self.question}\n'
        for answer in self.answers:
            to_return += f'\t-\t{answer[0]} which is {answer[1]}\n'
        return to_return 




class Quiz:
    def __init__(self, user_id: int):
        self.API_ROOT = 'http://54.205.150.68:3000/'
        self.name = 'Error, no quiz name set'
        self.questions = [] # list of questions (full question text and answers)
        self.user_id = user_id

    def read_quiz_from_database(self, quiz_id):
        pass

    def get_next_quiz_id(self) -> int:
        '''read from the database to get the next sequential quiz ID.'''
        endpoint = self.API_ROOT + 'quiz?select=quiz_id&order=quiz_id.desc&limit=1'
        response = requests.get(endpoint).json()[0]['quiz_id'] + 1
        return response

    def get_questions(self, quiz_id) -> list:
        '''Return a list of quiz questions based on the quiz ID'''
        endpoint = self.API_ROOT + 'quiz' + f'?quiz_id=eq.{quiz_id}'
        api_response = requests.get(endpoint)
        print(f'QUIZ RESPONSE: {api_response}')
        if api_response.json():
            body = api_response.json()[0]
        # read from database

    def save_quiz_to_database(self):
        endpoint = self.API_ROOT + 'quiz' + f'?quiz_id=eq.{quiz_id}'
        api_response = requests.get(endpoint)




def main():
    my_question = Question('What color is the sky?')
    my_question.add_answer('blue', True)
    my_question.add_answer('red', False)
    my_question.add_answer('pink', False)
    my_question.add_answer('green', False)
    print(my_question)

    my_quiz = Quiz('6')




    print(f'Next Quiz ID: {my_quiz.get_next_quiz_id()}')


if __name__ == '__main__':
    main()