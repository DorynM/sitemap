import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import Tree
from threading import Thread
import time


int_url = set()
checked_url = set()
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Chrome/53.0.2785.116 Safari/537.36 '
                  'OPR/40.0.2308.81',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/webp,*/*;q=0.8',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, lzma, sdch',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'
}


def valid_url(url):
    """
    Функция проверяет, действительна ли ссылка
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def writeURLtoTree(href, tree, urls, parent):
    """
    Функция добавляет новую ссылку в дерево, если её не было в нём
    """
    global int_url

    if href[0:5] == 'http:':
        if href not in int_url:
            href = 'https' + href[4:]
            if href not in int_url:
                href = 'http' + href[5:]
                try:
                    tree.add(href, parent)
                    urls.add(href)
                    int_url.add(href)
                except ValueError:
                    pass

    elif href[0:5] == 'https':
        if href not in int_url:
            href = 'http' + href[5:]
            if href not in int_url:
                href = 'https' + href[4:]
                try:
                    tree.add(href, parent)
                    urls.add(href)
                    int_url.add(href)
                except ValueError:
                    pass


def searchParentURL(href, tree, urls, start_url):
    """
    Функция определяет родительскую ссылку
    """
    parent = href.split("/")
    for i in range(1, len(parent) - 2):
        grandparent = "/".join(parent[:-i])
        resp = requests.get(grandparent,
                            headers=headers, timeout=2.5)

        if not resp.status_code <= 299:
            if i - 1:
                grandparent = "/".join(parent[
                                       :-(i - 1)])
            else:
                grandparent = "/".join(parent)
            writeURLtoTree(grandparent, tree, urls, start_url)
            break
        elif urlparse(grandparent).path == "":
            grandparent = "/".join(parent[:-(i - 1)])
            writeURLtoTree(grandparent, tree, urls, start_url)
            break


def checkURL(href, domain_name, url, tree, urls, start_url):
    """
    Функция проверяет, является ссылка внутреней или внешней
    """
    if valid_url(href):
        if href[-1] == '/':
            href = href[0:-1]
        if href not in int_url:
            if domain_name in href:
                if not urlparse(href).path == "":
                    parent = href[:href.rfind('/')]
                else:
                    parent = href

                if parent == url:
                    writeURLtoTree(href, tree, urls, parent)
                else:
                    if not urlparse(href).path == "":
                        if len(int_url) < 200000:
                            searchParentURL(href, tree, urls, start_url)
                    else:
                        writeURLtoTree(href, tree, urls, start_url)
    return


def website_links(url, tree, start_url):
    """
    Функция находит все ссылки веб-страницы
    """
    global int_url

    urls = set()
    domain_name = urlparse(url).netloc

    try:
        r = requests.get(url, headers=headers, timeout=2.5)
    except:
        return urls

    if 'text/html' in r.headers['content-type']:
        try:
            soup = BeautifulSoup(r.content, "html.parser")
        except:
            return urls

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if not (href == "" or href is None):
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                href = "{0}://{1}{2}".format(parsed_href.scheme,
                                             parsed_href.netloc,
                                             parsed_href.path)

            checkURL(href, domain_name, url, tree, urls, start_url)

        return urls
    else:
        return urls


def crawl(url, tree, max_height, start_url):
    """
    Функция просматривает веб-страницу и извлекает из неё ссылки
    """
    global threads, int_url, checked_url
    try:
        links = website_links(url, tree, start_url)
    except:
        links = set()

    print(len(threads))
    for link in links:
        if len(int_url) < 200000:
            if link not in checked_url:
                if tree.find_height(heights=set()) - tree.find_leaf(link).\
                        find_height(heights=set()) < max_height:
                    checked_url.add(link)
                    thread = Thread(target=crawl, args=(link, tree, max_height,
                                                        start_url))
                    threads.append(thread)
                    thread.start()


def generateSitemapFile(fileName, tree):
    """
    Функция записываает в файл данные из дерева
    """
    fw = open(fileName, 'w', encoding='utf-8')

    fw.write('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n''')
    for leaf in tree:
        fw.write('  <url>\n  '
                 '  <loc>{0}</loc>\n'.format(leaf.value))
        fw.write('  </url>\n')
    fw.write('</urlset>')

    fw.close()


if __name__ == "__main__":
    threads = []
    max_depth = int(input("Введите глубину поиска: "))
    initial_url = input("Введите URL: ")
    any_tree = Tree.Tree(initial_url)
    int_url.add(initial_url)
    filename = input("Введите имя файла: ") + ".txt"
    startTime = time.time()

    crawl(initial_url, any_tree, max_depth, initial_url)

    for item in threads:
        item.join()

    endTime = time.time()
    print("\nКоличество найденых ссылок:", len(int_url))
    print("Время работы программы:", round(endTime - startTime, 2), "с")

    print("\nДерево карты сайта:", initial_url, "\n")
    any_tree.printTree()

    generateSitemapFile(filename, any_tree)
    print("\n<<Файл создан>>")
