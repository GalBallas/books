import requests

import pandas as pd

# read ISBNs from file
with open('books-isbns.txt', 'r') as f:
    isbns = f.read().splitlines()

# fetch data for each ISBN and store in a list
books_data = []
for isbn in isbns:
    url = f'https://openlibrary.org/isbn/{isbn}.json'
    try:
        response = requests.get(url, timeout=2)
        data = response.json()
        if data:
            books_data.append(data[f'ISBN:{isbn}'])
    except:
        pass

# create a DataFrame from the list of books data
books_df = pd.DataFrame(books_data)

# count the number of unique book titles
num_books = books_df['title'].nunique()

print(f'There are {num_books} different books in the list.')



df = df[df.index.str.startswith('ISBN:')]  # remove rows with missing data
df = df.drop(columns=['bib_key', 'info_url', 'preview', 'preview_url', 'thumbnail_url'])  # remove unnecessary columns
df.index = df.index.str.replace('ISBN:', '')  # clean up index
df = df.reset_index().rename(columns={'index': 'ISBN'})  # reset index and rename columns
df['title'] = df['title'].str.replace(' : a novel', '')  # remove subtitle from title

df['publication_year'] = pd.to_datetime(df['publish_date'], errors='coerce').dt.year

top_author = df['authors'].explode().value_counts().index[0]

top_author_books = df[df['authors'].explode() == top_author].sort_values(by='publication_year')
second_title = top_author_books.iloc[1]['title']

top_publisher_author = df.groupby(['publishers', 'authors']).size().idxmax()

print(
    f"The title of the second published book for the author with the highest number of different titles in the list is '{second_title}'")
print(f"The pair of (publisher, author) with the highest number of books published is {top_publisher_author}")
