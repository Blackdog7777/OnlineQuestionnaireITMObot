import telebot
import sqlite3
import ast
from config import token

client = telebot.TeleBot(token)

connection = sqlite3.connect('survey.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS survey(
        uid INT,
        sid INT,
        questions TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS answers(
        uid INT,
        sid INT,
        answers TEXT
)""")


@client.message_handler(commands=['start'])
def start(message):
    mci = message.chat.id
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    client.send_message(mci,
                        "Это бот для создания опросов, на которые может ответить каждый пользователь\nЧтобы посмотреть список всех команд: \n /create_survey - создать новый опрос\n /view - просмотр всех доступных опросов\n /view_answers -  посмотреть все ответы на ваш опрос\n /select_survey - присоединиться к опросу\n /delete_survey - удалить ваш опрос\n /git - ссылка на репозиторий Git\n /docs - ссылка на документацию")


@client.message_handler(commands=['create_survey'])
def create_survey(message):
    mci = message.chat.id
    msg = message.text.split()[1:]
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    if len(msg) == 0:
        client.send_message(mci,
                            "Чтобы создать опрос используйте команду \n/create_survey {Сюда пишите 1й вопрос}? {Сюда пишите 2й вопрос}? ...")
    else:
        loc_connection = sqlite3.connect('survey.db')
        loc_cursor = loc_connection.cursor()
        stringOfQuestions = ''
        for i in msg:
            stringOfQuestions += i
            stringOfQuestions += ' '
        stringOfQuestions = stringOfQuestions.split("? ")
        if stringOfQuestions[-1] == '':
            stringOfQuestions.remove(stringOfQuestions[-1])
        lastID = 0
        for i in loc_cursor.execute("SELECT * FROM survey"):
            lastID = int(i[1])
        lastID += 1
        loc_cursor.execute(f'INSERT INTO survey VALUES ({mci}, {lastID}, "{stringOfQuestions}")')
        loc_connection.commit()
        client.send_message(mci, f"Ваш опрос добавлен\nID опроса: {lastID}")


@client.message_handler(commands=['view'])
def view(message):
    mci = message.chat.id
    msg = message.text.split()[1:]
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    questions = ''
    loc_connection = sqlite3.connect('survey.db')
    loc_cursor = loc_connection.cursor()
    questionsList = ''
    for i in loc_cursor.execute("SELECT * FROM survey"):
        questionID = int(i[1])
        questions = i[2]
        questions = ast.literal_eval(questions)
        temp = ''
        for i in questions:
            temp += i
            temp += '? '
        questionsList += f'№{questionID}\nPreview: {temp}\n'
    client.send_message(message.chat.id, f"Список доступных опросов: \n{questionsList}")


@client.message_handler(commands=['select_survey'])
def select_survey(message):
    mci = message.chat.id
    if len(message.text.split()) >= 3:
        msg = message.text.split()[2:]
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    if 1 <= len(message.text.split()) < 3:
        print(len(message.text.split()))
        client.send_message(mci,
                            "Что бы присоединиться к опросу используйте комманду: \n/select_survey {ID опроса} {Ответ 1}. {Ответ 2}. и тд")
    if len(message.text.split()) >= 3:
        surveyId = message.text.split()[1]
        if not surveyId.isalpha():
            loc_connection = sqlite3.connect('survey.db')
            loc_cursor = loc_connection.cursor()
            string_of_answers = ''
            for i in msg:
                string_of_answers += i
                string_of_answers += ' '
            string_of_answers = string_of_answers.split(". ")
            if string_of_answers[-1] == '':
                string_of_answers.remove(string_of_answers[-1])
            trigger = False
            for i in loc_cursor.execute("SELECT * FROM survey"):
                if str(i[1]) == surveyId:
                    trigger = True
            if trigger:
                loc_cursor.execute(f'INSERT INTO answers VALUES ({mci}, {surveyId}, "{string_of_answers}")')
                loc_connection.commit()
                client.send_message(mci, f"Ваши ответы сохранены!")
            else:
                client.send_message(mci, f"Такого опроса не найдено")
        else:
            client.send_message(message.chat.id, f"В номере опроса не может быть букв")


@client.message_handler(commands=['delete_survey'])
def delete_survey(message):
    mci = message.chat.id
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    if len(message.text.split()) == 1:
        print(len(message.text.split()))
        client.send_message(mci,
                            "Что бы удалить опрос используйте комманду: \n/delete_survey {ID опроса}")
    else:
        surveyId = message.text.split()[1]
        if not surveyId.isalpha():
            loc_connection = sqlite3.connect('survey.db')
            loc_cursor = loc_connection.cursor()
            string_of_answers = ''
            loc_cursor.execute(f"DELETE FROM survey WHERE uid = {mci} AND sid = {surveyId}")
            loc_connection.commit()
            client.send_message(mci,
                                f"Все ваши опросы с ID {surveyId} удалены")
        else:
            client.send_message(message.chat.id, f"В номере опроса не может быть букв")


@client.message_handler(commands=['view_answers'])
def view_answers(message):
    if len(message.text.split()) >= 2:
        mci = message.chat.id
        msg = message.text.split()[1:]
        if not message.text.split()[1].isalpha():
            sid = int(message.text.split()[1])
            print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
            questions = ''
            loc_connection = sqlite3.connect('survey.db')
            loc_cursor = loc_connection.cursor()
            questionsList = ''
            for i in loc_cursor.execute(f"SELECT * FROM answers WHERE uid = {mci} AND sid = {sid}"):
                questionID = int(i[0])
                questions = i[2]
                questions = ast.literal_eval(questions)
                temp = ''
                for i in questions:
                    temp += i
                    temp += '. '
                questionsList += f'№{questionID}\nPreview: {temp}\n'
            client.send_message(message.chat.id, f"Список ответов на опрос №{sid}: \n{questionsList}")
        else:
            client.send_message(message.chat.id, f"В номере опроса не может быть букв")
    else:
        client.send_message(message.chat.id,
                            "Что бы просмотреть все ответы на опрос используйте комманду: \n/view_answers {ID опроса}")


@client.message_handler(commands=['git'])
def git(message):
    mci = message.chat.id
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    client.send_message(message.chat.id, f"Ссылка: https://github.com/Blackdog7777/OnlineQuestionnaireITMObot")


@client.message_handler(commands=['docs'])
def docs(message):
    mci = message.chat.id
    print(f"[LOG] used command {message.text.split()[:]} in chatID: {mci}")
    client.send_message(message.chat.id, f"Ссылка: https://github.com/Blackdog7777/OnlineQuestionnaireITMObot/blob/main/README.md")


client.polling(none_stop=True, interval=0)
