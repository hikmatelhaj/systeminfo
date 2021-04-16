from configparser import ConfigParser
import os
from datetime import date
import tkinter.messagebox
import tkinter as tk


file = "projectini.ini"
con = ConfigParser()
con.read(file)

root = tk.Tk()
root.overrideredirect(1)  # this will prevent another application opening, the tkinter module wants to open this by default
root.withdraw()


def logger(tekst, enter):
    try:
        logfile = open(con["DEFAULT"]["file_out_logger"], "a")
        logfile.write(tekst)
        if enter:
            logfile.write("\n")
        logfile.close()
    except OSError:
        tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["error2"])


def show_date():
    today = date.today()
    print("Today's date:", today)
    logger(str(today), False)


logger("------------------------------------------- ", False)  # to seperate it from everytime you open it
show_date()
logger(" -------------------------------------------", True)

array_of_dictionaries = []


def check_parts(arr):
    try:
        dict = {}
        dict["Level"] = arr[0].strip()
        dict["Date"] = arr[1].strip()
        dict["Source"] = arr[2].strip()
        dict["id"] = int(arr[3].strip())
        dict["type"] = arr[4].strip()
        if len(arr) > 6:
            together = ""
            for i in range(0, len(arr) - 1):
                if i >= 5:
                    together += arr[i].strip()
            dict["task"] = together
        else:
            dict["task"] = arr[5].strip()
        array_of_dictionaries.append(dict)
    except IndexError:
        tkinter.messagebox.showwarning(title="Error!", message=con["constants"]["error_index"])


def put_together(arr):
    # putting the last elements together of the array in case there are commas in the string
    together = ""
    new_arr = []
    for i in range(0, len(arr)):
        if i >= 5:
            together += arr[i].strip()
        else:
            new_arr.append(arr[i])
    new_arr.append(together)
    return new_arr


def read_file(file):
    try:
        counter = 0
        begin_string = ""
        counter_info = 0
        counter_warning = 0
        counter_error = 0
        last_known_line_array = []
        keywords = ["information", "warning", "error"]
        for line in file:
            if line.strip() != "":  # if lines are not empty
                counter += 1
                if counter != 1:  # filter the first line
                    line_array = line.split(",")
                    if con["constants"]["info"].lower() in line.lower():
                        counter_info += 1
                    elif con["constants"]["warning"].lower() in line.lower():
                        counter_warning += 1
                    elif con["constants"]["error"].lower() in line.lower():
                        counter_error += 1
                    if (line_array[-1].strip()[-1] != '"' and line_array[-1].strip()[0] != '"') and len(
                            line_array) == 6:  # means the full string is on 1 line (no "" and it can be only on the last line)
                        # also no kommas in the string, with string I mean the value of the task in dictionary
                        check_parts(line_array)
                    elif line_array[-1].strip()[0] == '"' and len(
                            line_array) == 6:  # uncompleted, the string isn't completed yet
                        last_known_line_array = line_array
                    elif len(line_array) > 6 and line_array[0].strip().lower() in keywords:  # a comma in the task string
                        line_array = put_together(line_array)
                        if line_array[-1].strip()[-1] == '"':  # no more lines after
                            check_parts(line_array)  # this can't be a line with a comma that ends on " because there is a minimum length
                            # we check if the first array element is one of the keywords
                            # in case it's not, there are 6 or more commas in a string file
                        else:  #
                            line_array = put_together(line_array)  # in case there are commas in the string
                            last_known_line_array = line_array  # unfinished string
                    elif len(line_array) == 1:  # part of the string
                        if line_array[0].strip()[-1] == '"':  # last character is a "
                            begin_string += line_array[0]
                            last_known_line_array.append(begin_string)
                            last_known_line_array = put_together(last_known_line_array)
                            check_parts(last_known_line_array)
                            begin_string = ""
                            last_known_line_array = ""
                        else:
                            begin_string += line_array[0]  # no ", so we just add it to the string
                    else:  # line is part of the string, but it has kommas
                        str1 = ""
                        for el in line_array:
                            str1 += el
                            str1 += ","
                        str1 = str1[:-1]  # delete last comma
                        begin_string += str1
        return counter, counter_info, counter_warning, counter_error
    except:
        tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["error"])


def sort1():
    new_list = []
    temp_copy = array_of_dictionaries
    while temp_copy:
        minimum = temp_copy[0]  # arbitrary number in list
        for x in temp_copy:
            # print(x.get("id"), minimum.get("id"))
            if x.get("id") < minimum.get("id"):
                minimum = x
        new_list.append(minimum)
        temp_copy.remove(minimum)
    return new_list


def sort2():
    new_list = []
    temp_copy = array_of_dictionaries
    minimum = temp_copy[0]
    while temp_copy:
        try:
            minimum = temp_copy[0]
            for x in temp_copy:
                date = x.get("Date").split(" ")[0]
                specific = date.split("-")
                time = x.get("Date").split(" ")[1].split(":")
                date2 = minimum.get("Date").split(" ")[0]
                specific2 = date2.split("-")
                time2 = x.get("Date").split(" ")[1].split(":")
                # if PM adding 12h (converting everything to 24h for easier sorting)
                last = x.get("Date").split(" ")[2]
                last2 = minimum.get("Date").split(" ")[2]
                if last.strip() == "PM":
                    time[0] = int(time[0]) + 12
                if last2.strip() == "PM":
                    time2[0] = int(time[0]) + 12
                if int(specific[2].strip()) <= int(specific2[2].strip()) and int(specific[1].strip()) <= \
                        int(specific2[1].strip()) and int(specific[0]) <= int(specific2[0]) \
                        and int(time[2].strip()) <= int(time2[2].strip()) and int(time[1].strip()) <= int(
                    time2[1].strip()) and \
                        int(time[0]) <= int(time2[0]):  # comparing time
                    minimum = x
        except:
            tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["errorint"])
        new_list.append(minimum)
        temp_copy.remove(minimum)
    return new_list


def write_file_helper(file, toprint):
    counter = 0
    limitation = 0
    can = False  # as many lines as the file has
    try:
        limitation = int(con["constants"]["max"])
        str1 = "User added a limitation of lines (max " + con["constants"]["max"] + " lines)"
        logger(str1, True)
        can = True  # restricted amount of lines
    except:
        can = False
    for line in toprint:  # printing elements of an array
        counter += 1
        if can and counter > limitation:
            break  # stop writing, putting a break to not do unnecessary work
        else:
            file.write(str(line) + "\n")


def write_file(file):
    file.write(con["constants"]["splitting"])
    str1 = "Username PC: " + os.getlogin() + " "
    file.write(str1)
    file.write(con["constants"]["splitting"] + "\n")

    counter = 0
    if con["constants"]["sorting"] == "1":
        # filtering on date
        logger("Filtering on id", True)
        toprint = sort1()
        write_file_helper(file, toprint)
    elif con["constants"]["sorting"] == "2":
        logger("Filtering on date", True)
        toprint = sort2()
        write_file_helper(file, toprint)
    elif con["constants"]["sorting"] == "3":
        logger("User didn't want to sort", True)
        write_file_helper(file, array_of_dictionaries)
    print("Done! Check out", con["DEFAULT"]["file_out"], "for the output")


def option1():
    try:
        logger(con["chosenoptions"]["option1_chosen"], True)
        file1 = open(con["DEFAULT"]["file_in"], "r")
        counter1, counter2, counter3, counter4 = read_file(file1)
        print("The input file has a total of", counter1, "lines after filtering the empty ones")
        print("The input file has", counter2, "info lines")
        print("The input file has", counter3, "warning lines")
        print("The input file has", counter4, "error lines")
        file1.close()
    except OSError:
        tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["error"])


def option2():
    logger(con["chosenoptions"]["option2_chosen"], True)
    try:
        file2 = open(con["DEFAULT"]["file_out"], "a")
        write_file(file2)
        file2.close()
    except OSError:
        tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["errorwr"])


def option3():
    logger(con["chosenoptions"]["option3_chosen"], True)
    counter = 0
    try:
        file3 = open(con["DEFAULT"]["file_out"], "r")
        for line in file3:
            print(line.strip())
            counter += 1
        file3.close()
        print("The output file has", counter, "lines")
    except OSError:
        tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["errorwrr"])


def option4():
    try:
        logger(con["chosenoptions"]["option4_chosen"], True)
        open(con["DEFAULT"]["file_out"], 'w').close()  # clearing the file
        print(con["menu"]["cleaned"])
    except IOError:
        options = input("> ")
        tkinter.messagebox.showwarning(title="Error!", message=con["menu"]["errorclean"])


def main_menu():
    print(con['menu']["main"], "\n")
    print(con["menu"]["option1"])
    print(con["menu"]["option2"])
    print(con["menu"]["option3"])
    print(con["menu"]["option4"], "\n")
    options = input("> ")
    can = False
    while options != "":
        if options == "1":
            option1()
            options = input("> ")  # adding this to let the user use multiple options
            can = True
        elif options == "2":
            if can:
                option2()
                options = input("> ")  # adding this to let the user use multiple options
            else:
                print(con["constants"]["not_processed"])
                options = input("> ")
        elif options == "3":
            option3()
            options = input("> ")
        elif options == "4":
            option4()
            # options = input("> ")
            options = input("> ")
        else:
            if options != "":
                options = input("> ")
            else:
                options = ""  # close it


main_menu()

# EXITED MENU, adding 1x \n to make the logger cleaner
logger("", True)
