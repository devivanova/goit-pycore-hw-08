from collections import UserDict
import re
from datetime import datetime
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        self.value = self.validate(value)

    def validate(self, value):
        if re.match(r'^\d{10}$', value):
            return value
        else:
            raise ValueError("Phone number must be 10 digits")


class Birthday(Field):
    def __init__(self, value):
        self.value = self.validate(value)

    def validate(self, value):
        try:
            birthday = datetime.strptime(value, '%d.%m.%Y')
            return birthday
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return True
        return False

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime(
            '%d.%m.%Y') if self.birthday else 'N/A'
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(
                    year=today.year)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Invalid command. Please provide correct arguments."
    return inner


@input_error
def add_contact(args, book):
    if len(args) != 2:
        raise ValueError("Invalid command. Usage: add [name] [phone]")
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return "Contact added."


@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError(
            "Invalid command. Usage: change [name] [old_phone] [new_phone]")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        if record.edit_phone(old_phone, new_phone):
            return "Contact updated."
        else:
            return "Phone number not found."
    else:
        raise KeyError("Contact not found.")


@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise ValueError("Invalid command. Usage: phone [name]")
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    else:
        raise KeyError("Contact not found.")


@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."
    return "\n".join([str(record) for record in book.data.values()])


@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError(
            "Invalid command. Usage: add-birthday [name] [birthday]")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError("Contact not found.")


@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Invalid command. Usage: show-birthday [name]")
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return record.birthday.value.strftime('%d.%m.%Y')
        else:
            return "Birthday not set."
    else:
        raise KeyError("Contact not found.")


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join([str(record) for record in upcoming_birthdays])


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file is not found


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
