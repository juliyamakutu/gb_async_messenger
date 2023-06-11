from rich.console import Console
from rich.panel import Panel
import subprocess
import chardet


console = Console()


# Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и
# проверить тип и содержание соответствующих переменных.
console.rule("[bold red]Задание 1 часть первая:[/bold red]")

first_word = 'разработка'
second_word = 'сокет'
third_word = 'декоратор'
console.print(f"Переменная {first_word=} имеет тип {type(first_word)}")
console.print(f"Переменная {second_word=} имеет тип {type(second_word)}")
console.print(f"Переменная {third_word=} имеет тип {type(third_word)}")

# Затем с помощью онлайн-конвертера преобразовать строковые представление в формат
# Unicode и также проверить тип и содержимое переменных.
console.rule("[bold red]Задание 1 часть вторая:[/bold red]")

first_word = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
second_word = '\u0441\u043e\u043a\u0435\u0442'
third_word = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

console.print(f"Переменная {first_word=} имеет тип {type(first_word)}")
console.print(f"Переменная {second_word=} имеет тип {type(second_word)}")
console.print(f"Переменная {third_word=} имеет тип {type(third_word)}")

# Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в
# последовательность кодов (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.
console.rule("[bold red]Задание 2:[/bold red]")

first_word = b'class'
second_word = b'function'
third_word = b'method'
console.print(f"Переменная {first_word=} имеет тип {type(first_word)}")
console.print(f"Переменная {second_word=} имеет тип {type(second_word)}")
console.print(f"Переменная {third_word=} имеет тип {type(third_word)}")

# Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
console.rule("[bold red]Задание 3:[/bold red]")

try:
    eval("b'attribute'")
except SyntaxError:
    console.print("Слово 'attribute' [red]невозможно[/red] записать в байтовом типе")
else:
    console.print("Слово 'attribute' возможно записать в байтовом типе")

try:
    eval("b'класс'")
except SyntaxError:
    console.print("Слово 'класс' [red]невозможно[/red] записать в байтовом типе")
else:
    console.print("Слово 'класс' возможно записать в байтовом типе")

try:
    eval("b'функция'")
except SyntaxError:
    console.print("Слово 'функция' [red]невозможно[/red] записать в байтовом типе")
else:
    console.print("Слово 'функция' возможно записать в байтовом типе")

try:
    eval("b'type'")
except SyntaxError:
    console.print("Слово 'type' [red]невозможно[/red] записать в байтовом типе")
else:
    console.print("Слово 'type' возможно записать в байтовом типе")

# Преобразовать слова «разработка», «администрирование», «protocol», «standard» из
# строкового представления в байтовое и выполнить обратное преобразование
# (используя методы encode и decode).
console.rule("[bold red]Задание 4:[/bold red]")

first_word = 'разработка'
second_word = 'администрирование'
third_word = 'protocol'
fourth_word = 'standard'
console.rule("[bold red]Задание 4 часть первая:[/bold red]")
console.print(f"Переменная {first_word=} имеет тип {type(first_word)}")
console.print(f"Переменная {second_word=} имеет тип {type(second_word)}")
console.print(f"Переменная {third_word=} имеет тип {type(third_word)}")
console.print(f"Переменная {fourth_word=} имеет тип {type(fourth_word)}")

first_word = first_word.encode(encoding='utf-8')
second_word = second_word.encode(encoding='utf-8')
third_word = third_word.encode(encoding='utf-8')
fourth_word = fourth_word.encode(encoding='utf-8')
console.rule("[bold red]Задание 4 часть вторая:[/bold red]")
console.print(f"Переменная {first_word=} имеет тип {type(first_word)}")
console.print(f"Переменная {second_word=} имеет тип {type(second_word)}")
console.print(f"Переменная {third_word=} имеет тип {type(third_word)}")
console.print(f"Переменная {fourth_word=} имеет тип {type(fourth_word)}")

first_word = first_word.decode(encoding='utf-8')
second_word = second_word.decode(encoding='utf-8')
third_word = third_word.decode(encoding='utf-8')
fourth_word = fourth_word.decode(encoding='utf-8')
console.rule("[bold red]Задание 4 часть третья:[/bold red]")
console.print(f"Переменная {first_word=} имеет тип {type(first_word)}")
console.print(f"Переменная {second_word=} имеет тип {type(second_word)}")
console.print(f"Переменная {third_word=} имеет тип {type(third_word)}")
console.print(f"Переменная {fourth_word=} имеет тип {type(fourth_word)}")

# Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать
# результаты из байтовового в строковый тип на кириллице.
console.rule("[bold red]Задание 5:[/bold red]")

args = ['ping', '-c', '3', 'yandex.ru']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_ping.stdout:
    console.print(line.decode('cp866').encode('utf-8').decode('utf-8'))

args = ['ping', '-c', '3', 'youtube.com']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in subproc_ping.stdout:
    console.print(line.decode('cp866').encode('utf-8').decode('utf-8'))

# Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор». Проверить кодировку
# файла по умолчанию. Принудительно открыть файл в формате Unicode и
# вывести его содержимое.
console.rule("[bold red]Задание 6:[/bold red]")
with open('test_file.txt', 'w', encoding='cp1251') as f:
    f.write('сетевое программирование\n')
    f.write('сокет\n')
    f.write('декоратор\n')

file = open('test_file.txt', 'rb')
console.print(f"Кодировка файла по умолчанию: {chardet.detect(file.read())['encoding']}")

with open('test_file.txt', 'r', encoding='utf-8') as f:
    try:
        console.print(Panel(f.read(), title='Содержимое файла принудительно открытого в формате Unicode'))
    except UnicodeDecodeError:
        console.print('Файл не может быть открыт в формате Unicode')