import requests
from bs4 import BeautifulSoup
import json
import time
import re

GENRE_MAPPING = {
    "детская литература: прочее": "Проза",
    "детская проза": "Проза",
    "детские остросюжетные": "Приключения", 
    "детские приключения": "Приключения",
    "детские стихи": "Стихи",
    "детский фольклор": "Сказка",
    "книга-игра": "Образовательная литература",
    "образовательная литература": "Образовательная литература",
    "подростковая литература": "Подростковая",
    "сказка": "Сказка"
}

def clean_genre(genre_text):
    if genre_text.startswith("Жанр: "):
        cleaned_genre = genre_text.replace("Жанр: ", "", 1).strip()
    else:
        cleaned_genre = genre_text.strip()
    genre_lower = cleaned_genre.lower()
    if genre_lower in GENRE_MAPPING:
        return GENRE_MAPPING[genre_lower]
    else:
        return cleaned_genre

def format_description(title, description):
    return f"{title}: {description}"

def clean_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'[^а-яА-ЯёЁ0-9\s\.,!?;:()\-—–«»""]', '', text)
    
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def scrape_books_from_page(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    books_data = []
    
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        book_blocks = soup.find_all('div', class_='bookView')
        
        for book in book_blocks:
            try:
                ul = book.find('ul')
                if not ul:
                    continue
                
                li_elements = ul.find_all('li')
                
                if len(li_elements) == 6:
                    title_elem = ul.find('li', class_='title')
                    title = title_elem.text.strip() if title_elem else ""
                    
                    title = clean_text(title)

                    genre_elem = li_elements[2] if len(li_elements) > 2 else None
                    genre_text = genre_elem.text.strip() if genre_elem and not genre_elem.get('class') else ""
                    
                    genre = clean_genre(genre_text)
                    
                    description_elem = li_elements[3] if len(li_elements) > 3 else None
                    original_description = description_elem.text.strip() if description_elem and not description_elem.get('class') else ""
                    
                    original_description = clean_text(original_description)
                    
                    formatted_description = format_description(title, original_description)
                    
                    if title and genre and original_description:
                        book_info = {
                            'genre': genre,
                            'description': formatted_description
                        }
                        books_data.append(book_info)
                    
                
            except Exception as e:
                print(f"Ошибка при обработке книги: {e}")
                continue
                
    except Exception as e:
        print(f"Ошибка при загрузке страницы {page_url}: {e}")
    
    return books_data

def scrape_all_books():
    base_url = "сайт"
    all_books = []
    
    page_num = 1
    
    while page_num <= 300: 
        if page_num == 1:
            page_url = f"{base_url}.html"
        else:
            page_url = f"{base_url}-{page_num}.html"
        
        books_on_page = scrape_books_from_page(page_url)
        
        if not books_on_page:
            print(f"На странице {page_num} не найдено подходящих книг. Возможно, это конец.")
            break
        
        all_books.extend(books_on_page)

        time.sleep(1)
        
        page_num += 1
    
    return all_books

def save_to_json(books_data, filename='children_books_dataset.json'):
    if not books_data:
        print("Нет данных для сохранения")
        return
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(books_data, file, ensure_ascii=False, indent=2, separators=(',', ': '))

def analyze_genres(books_data):
    genre_count = {}
    for book in books_data:
        genre = book['genre']
        genre_count[genre] = genre_count.get(genre, 0) + 1
    
    print("\nРаспределение жанров:")
    for genre, count in sorted(genre_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {genre}: {count} книг")

def main():
    all_books = scrape_all_books()
    
    if all_books:
        save_to_json(all_books, 'children_books_dataset.json')
        
        print("\nСтатистика:")
        print(f"Всего собрано книг: {len(all_books)}")
        analyze_genres(all_books)
    else:
        print("Не удалось собрать данные")

if __name__ == "__main__":
    main()
