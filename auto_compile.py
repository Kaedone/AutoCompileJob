import os
import subprocess
from git import Repo
from PyPDF2 import PdfFileMerger, PdfFileReader


# функция для извлечения переменных из enviroment
def get_env_var(name):
    if name in os.environ:
        return os.environ[name]
    else:
        raise Exception("{} not found in environment variables".format(name))


# Путь к локальному репозиторию
REPO_PATH = get_env_var("REPO_PATH")

# Путь к папке с исходными файлами
SOURCE_PATH = get_env_var("SOURCE_PATH")

# Путь к папке с скомпилированными файлами
OUTPUT_PATH = get_env_var("OUTPUT_PATH")

# Название ветки, за изменениями которой следим
BRANCH_NAME = get_env_var("BRANCH_NAME")

# Команда для компиляции исходных файлов
COMPILE_COMMAND = "pdflatex -output-directory={} {}"


# Функция для компиляции файла в формат PDF
def compile_to_pdf(file_name):
    # Имя файла без расширения
    basename = os.path.splitext(file_name)[0]

    # Путь к исходному файлу
    source_file = os.path.join(SOURCE_PATH, file_name)

    # Путь к выходному файлу
    output_file = os.path.join(OUTPUT_PATH, basename + ".pdf")

    # Команда для компиляции файла
    command = COMPILE_COMMAND.format(OUTPUT_PATH, source_file)

    # Запускаем процесс компиляции
    subprocess.run(command, shell=True, cwd=SOURCE_PATH)

    return output_file


# Функция для объединения нескольких PDF-файлов в один
def merge_pdfs(filenames, output_file):
    merger = PdfFileMerger()
    for file_name in filenames:
        with open(file_name, "rb") as f:
            merger.append(PdfFileReader(f))
    with open(output_file, "wb") as f:
        merger.write(f)


# Инициализируем репозиторий
repo = Repo(REPO_PATH)

# Получаем текущую ветку
branch = repo.head.reference

while True:
    # Проверяем изменения в репозитории
    if branch.name == BRANCH_NAME and branch.commit != repo.head.commit:
        print("New changes detected, compiling...")

        # Получаем список измененных файлов
        diff = repo.git.diff("--name-only", branch.commit, repo.head.commit).split()

        # Компилируем каждый из измененных файлов
        pdf_files = []
        for filename in diff:
            if os.path.splitext(filename)[1] in [".tex", ".bib"]:
                pdf_file = compile_to_pdf(filename)
                pdf_files.append(pdf_file)

            # Объединяем PDF-файлы в один
            if pdf_files:
                output_file = os.path.join(OUTPUT_PATH, "output.pdf")
                merge_pdfs(pdf_files, output_file)
                print("Compilation finished, output file: {}".format(output_file))

            # Обновляем указатель на последний коммит
            branch.commit = repo.head.commit

# Ждем некоторое время перед следующей проверкой изменений
time.sleep(60)