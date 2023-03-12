import requests
import pandas as pd

BOOKS_ISBNS_TXT = "/Users/galballas/src/books/books-isbns.txt"
OPEN_LIBRARY_URL = lambda isbn: f"https://openlibrary.org/isbn/{isbn}.json"
DOWNLOADED_DATA_CSV = "/Users/galballas/src/books/books.csv"


def get_books_data(books_isbns_path, target_file):
    books_data = []
    with open(books_isbns_path) as f:
        for i, line in enumerate(f):
            isbn = line.strip()
            try:
                url = OPEN_LIBRARY_URL(isbn)
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    book_data: dict = response.json()
                    book_data.update({'isbn': isbn})
                    books_data.append(book_data)
                    print(f"Finished processing book {i + 1}")
                else:
                    print('error accessing url', url, response.status_code, response.json())
            except Exception as e:
                print(f"Exception accessing file {url}", e)

    df = pd.DataFrame(books_data, index=None)
    df.to_csv(target_file)
    return books_data


books = get_books_data(BOOKS_ISBNS_TXT, DOWNLOADED_DATA_CSV)

df = pd.read_csv(DOWNLOADED_DATA_CSV)

# How many different books are in the list?
unique_books = len(df.drop_duplicates(subset=['title']))
print(f'There are: {unique_books} unique books in the list')

# What is the book with the most number of different ISBNs?
book_with_most_isbn = \
    df[['isbn', 'title']].groupby('title').count().reset_index().sort_values(by='isbn', ascending=False).iloc[0]
print(f'The book with the most number of different ISBNs is: "{book_with_most_isbn}.')

# How many books don’t have a goodreads id?
import json

df_unique = df.drop_duplicates(subset=['title'])
books_with_goodreads_id = df_unique['identifiers'].dropna() \
    .apply(lambda c: c.replace("'", '"')) \
    .apply(json.loads) \
    .apply(lambda c: 1 if 'goodreads' in c else 0) \
    .sum()

print(f'There are {books_with_goodreads_id} books without a goodreads id.')

# How many books have more than one author?
authors_per_title_df = df[['title', 'authors']].groupby('title').count().reset_index()
num_of_books_with_multi_authors = len(authors_per_title_df[authors_per_title_df['authors']>1])

print(f'There are {num_of_books_with_multi_authors} books with more than one author.')

# What is the number of books published per publisher?
result = df.groupby('publishers').size().reset_index(name='books_published')
result = result.sort_values(by='books_published', ascending=False)

print(f'The number of books published per publisher: /n  {result}')

# What is the median number of pages for books in this list?
median_pages = df['number_of_pages'].median()

print(f'The median number of pages per book is: {median_pages}.')

# What is the month with the most number of published books?
df['publication_date'] = pd.to_datetime(df['publish_date'], format='%B %d, %Y', errors='coerce')
result = df.groupby(df['publication_date'].dt.strftime('%m')).size().reset_index(name='books_published')
max_month = result.loc[result['books_published'].idxmax()]
print(f'The month with the most number of published books is {max_month["publication_date"]}, with {max_month["books_published"]} books published.')


# What is/are the longest word/s that appear/s either in a book’s description or in the first sentence of a book? In which book (title) it appears?
import re

longest_words = {}

for index, row in df.iterrows():
    description = str(row['description'])
    first_sentence = str(row['first_sentence']).split('.')[0]

    description = re.sub(r'[^\w\s]', '', description).lower()
    first_sentence = re.sub(r'[^\w\s]', '', first_sentence).lower()

    desc_words = description.split()
    fs_words = first_sentence.split()

    longest_desc_word = max(desc_words, key=len)
    longest_fs_word = max(fs_words, key=len)
    longest_words[row['title']] = {
        'description': longest_desc_word,
        'first_sentence': longest_fs_word
    }

longest_desc_book = max(longest_words.items(), key=lambda x: len(x[1]['description']))[0]
longest_desc_word = longest_words[longest_desc_book]['description']

longest_fs_book = max(longest_words.items(), key=lambda x: len(x[1]['first_sentence']))[0]
longest_fs_word = longest_words[longest_fs_book]['first_sentence']

print(
    f"The longest word in a book description is '{longest_desc_word}' and it appears in the book '{longest_desc_book}'.")
print(
    f"The longest word in the first sentence of a book is '{longest_fs_word}' and it appears in the book '{longest_fs_book}'.")

# What was the last book published in the list?
df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")
df["publish_year"] = df["publish_date"].dt.year
df["publish_month"] = df["publish_date"].dt.month

books_df = df.sort_values("publish_date")

last_book = books_df.iloc[-1]["title"]
print(f"The last book published in the list is '{last_book}'.")

# What is the year of the most updated entry in the list?
df_clean = df.dropna(subset=['last_modified'])
df_clean['year'] = pd.to_datetime(df_clean['last_modified']).dt.year
max_last_modified = df_clean['last_modified'].max()
year_of_most_updated_entry = max_last_modified.year

print(f"The year of the most updated entry is {year_of_most_updated_entry}")

# What is the title of the second published book for the author with the highest number of different titles in the list?
df.dropna(subset=['title', 'authors'], inplace=True)
author_counts = df.groupby('authors')['title'].nunique()
top_author = author_counts.idxmax()
top_author_books = df[df['authors'] == top_author].sort_values(by='publish_date')
second_book = top_author_books.iloc[1]['title']

print(f"The title of the second published book for {top_author} is '{second_book}'")

# What is the pair of (publisher, author) with the highest number of books published?
publisher_author_counts = df.groupby(['publisher', 'authors'])['title'].count()
top_pair = publisher_author_counts.idxmax()

print(f"The pair with the highest number of books published is ({top_pair[0]}, {top_pair[1]})")



