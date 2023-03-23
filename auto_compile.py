import os
import subprocess
import time
from git import Repo
from PyPDF2 import PdfFileMerger, PdfFileReader

# Путь к локальному репозиторию
REPO_PATH = "/path/to/repo"

# Путь к папке с исходными файлами
SOURCE_PATH = "/path/to/repo/source"

# Путь к папке с скомпилированными файлами
OUTPUT_PATH = "/path/to/repo/output"

# Название ветки, за изменениями которой следим
BRANCH_NAME = "master"

# Команда для компиляции исходных файлов
COMPILE_COMMAND = "pdflatex -output-directory={} {}"

# Функция для компиляции файла в формат PDF
def compile_to_pdf(filename):
    # Имя файла без расширения
    basename = os.path.splitext(filename)[0]

    # Путь к исходному файлу
    source_file = os.path.join(SOURCE_PATH, filename)

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
    for filename in filenames:
        with open(filename, "rb") as f:
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

