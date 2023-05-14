from words import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import math
import keyboard

global games_played, game_mode, amount_games, amount_guesses

start_button = 'esc'
options = Options()
options.add_experimental_option("detach", True)
games_played = 0
amount_guesses = []

browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

browser.get("https://wordle.jonyork.net")

browser.maximize_window()
game_mode = input("Two player or one player wordle? (respond with 'one' or 'two') ")
if game_mode == "one":
    amount_games = int(input("How many games would you like to play? "))
keyboard.wait(start_button)

submit = browser.find_element("id", "submit")
text_field = browser.find_element("id", "guessInput")


def rowGrabber(level):
    eval = [0, 0, 0, 0, 0]
    cells = browser.find_elements(By.CLASS_NAME, "letter")
    color_list = []
    for cell in cells:
        color = cell.value_of_css_property("background-color").strip("rgba()")
        color = color[0:color.rfind(",")]
        color_list.append(color)
    if level == 1:
        row_colors = color_list[0:5]
    if level == 2:
        row_colors = color_list[5:10]
    if level == 3:
        row_colors = color_list[10:15]
    if level == 4:
        row_colors = color_list[15:20]
    if level == 5:
        row_colors = color_list[20:25]
    if level == 6:
        row_colors = color_list[25:30]
    for i in range (0, 5):
        if row_colors[i] == '181, 159, 59':
            eval[i] = 2
        if row_colors[i] == '83, 141, 78':
            eval[i] = 1
        if row_colors[i] == '58, 58, 60':
            eval[i] = 0
    return eval


def solve(word):
    text_field.send_keys(word)
    print(word)
    keyboard.press('enter')
    time.sleep(0.2)


def bitsOfInformation(answers, word, eval, answer_bits):
    filtered_answers = answers.copy()
    original_length = len(answers)
    for i in range(0, 5):
        color = eval[i]
        for answer in answers:
            if color == 1:  # If color == green
                if answer[i] == word[i]:
                    continue
            elif color == 2: # If color == yellow
                counter = answer.count(word[i])
                if word[i] != answer[i]:
                    if counter != 0:
                        continue
            elif color == 0: # If color == gray
                if word[i] not in answer:
                    if answer == "ether":
                        print(word[i])
                    continue
                if word.count(word[i]) > answer.count(word[i]):
                    if answer == "ether":
                        print(word[i])
                    continue
            if answer in filtered_answers:
                filtered_answers.remove(answer)
    cut_length = len(filtered_answers)
    possibilities_cut = cut_length / original_length
    if answer_bits:
        if possibilities_cut == 0:
            return 0
        return -math.log(possibilities_cut, 2)
    return filtered_answers


def evaluate(guess, answer):
    result = [0] * 5
    masked_answer = list(answer)
    for i, letter in enumerate(guess):
        if letter == answer[i]:
            result[i] = 1
            masked_answer[i] = ' '
        elif letter in masked_answer:
            result[i] = 2
            masked_answer[masked_answer.index(letter)] = ' '
    return result


def guessPicker(narrowed):
    list = narrowed_list
    if narrowed == False:
        list = answer_words
        print("WE ARE USING ANSWER_WORDS!!!!")
    word_list_bits = []

    if len(narrowed_list) == 1:
        return narrowed_list[0]
    print(narrowed_list)
    for word_to_guess in list:
        word_list_avg = []
        for possible_answer in narrowed_list:
            word_list_avg.append(bitsOfInformation(narrowed_list, word_to_guess, evaluate(word_to_guess, possible_answer), answer_bits=True))
        #print(word_list_avg)
        word_list_bits.append(sum(word_list_avg) / len(word_list_avg))
        #print(f"Word List Bits: {word_list_bits}")
    index = word_list_bits.index(max(word_list_bits))
    #print(f"Bits predicted cut: {word_list_bits[index]}")
    return list[index]


def isWin(level):
    if rowGrabber(level) == [1, 1, 1, 1, 1]:
        return True
    return False


def again():
    global games_played, amount_games, game_mode, amount_guesses

    games_played += 1
    if game_mode == "one":
        again = browser.find_element("id", "againBtn")
        again.click()
        if games_played == amount_games:
            print(f"You have now played {games_played} games!")
            average_guess = sum(amount_guesses)/len(amount_guesses)
            print(f"Your average amount of guesses per word was {average_guess}")
            exit()
        else:
            print(f"You have now played {games_played} games!")
            average_guess = sum(amount_guesses) / len(amount_guesses)
            print(f"Your average amount of guesses per word was {average_guess}")
            main()
    elif game_mode == "two":
        again = browser.find_element(By.XPATH, '//button[text()="OK"]')
        again.click()
        again = browser.find_element("id", "againBtn")
        again.click()
        element = browser.find_element('id', 'link')
        while True:
            if element.is_displayed() == False:
                break
        main()

    else:
        exit()


def main():
    global narrowed_list, amount_guesses
    narrowed_list = answer_words
    solve("crane")
    if isWin(1):
        print("We won!")
        amount_guesses.append(1)
        again()
    first_level = rowGrabber(1)
    print(first_level)
    narrowed_list = bitsOfInformation(narrowed_list, "crane", first_level, answer_bits=False)
    if first_level in cases_tested:
        #print("I took the shortcut!!!")
        #print(first_level)
        #print(rowGrabber(1))
        #print(cases_tested.index(first_level))
        solve(cases_answers[cases_tested.index(first_level)])
        if isWin(2):
            print("We won!")
            amount_guesses.append(2)
            again()
        try:
            ok = browser.find_element(By.XPATH, '//button[text()="OK"]')
            ok.click()
        except:
            pass
        narrowed_list = bitsOfInformation(narrowed_list, cases_answers[cases_tested.index(first_level)], rowGrabber(2), answer_bits=False)
        lower_bound = 3
        #print(f"Narrowed List: {narrowed_list}")
    else:
        #print(f"Narrowed List: {narrowed_list}")
        lower_bound = 2
    for i in range (lower_bound, 7):
        if i > 3:
            word = guessPicker(narrowed=False)
        else:
            word = guessPicker(narrowed=True)
        try:
            ok = browser.find_element(By.XPATH, '//button[text()="OK"]')
            ok.click()
            again()
        except:
            pass
        solve(word)
        if isWin(i):
            amount_guesses.append(i)
            print("We won!")
            again()
        #print(f"Narrowed list: {narrowed_list}")
        #print(f"Image Grabber: {rowGrabber(i)}")
        #print(f"Actual bits cut: {bitsOfInformation(narrowed_list, word, rowGrabber(i), answer_bits=True)}")
        narrowed_list = bitsOfInformation(narrowed_list, word, rowGrabber(i), answer_bits=False)


if __name__ == '__main__':
    main()