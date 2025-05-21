from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np
import urllib.parse
import pandas as pd


top50= pickle.load(open("top_50.pkl","rb"))
reviews = pd.read_csv("popular_books_reviews_with_rating.csv")
REVIEWS_CSV = "popular_books_reviews_with_rating.csv"

app = Flask(__name__)



pt=pickle.load(open("pt.pkl",'rb'))
books=pickle.load(open("books.pkl",'rb'))
similarity=pickle.load(open("similarity.pkl",'rb'))
book_list = list(top50['Book-Title'].unique())
np.random.shuffle(book_list)


@app.route('/')
def index():
    return render_template('index.html',
                           book_name =list(top50['Book-Title'].values),
                           author=list(top50['Book-Author'].values),
                           image=list(top50['Image-URL-M'].values),
                           votes=list(top50['no-rating'].values),
                           rating=list(top50['avg-rating'].values)
    )
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html', book_list=book_list)

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    if user_input not in pt.index:
        # Handle invalid book input gracefully
        return render_template('recommend.html', data=0, book_list=book_list)

    index = np.where(pt.index == user_input)[0][0]
    similarity_scores = list(enumerate(similarity[index]))
    sorted_books = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[0:24]  # top 5

    recommendations = []
    for i in sorted_books:
        book_title = pt.index[i[0]]
        book_data = books[books['Book-Title'] == book_title].drop_duplicates('Book-Title')

        if not book_data.empty:
            title = book_data['Book-Title'].values[0]
            author = book_data['Book-Author'].values[0]
            image_url = book_data['Image-URL-M'].values[0]
            recommendations.append([title, author, image_url])


    return render_template('recommend.html', data=recommendations, book_list=book_list)




@app.route('/book/<path:title>')
def book_detail(title):
    title = urllib.parse.unquote(title)  # Decode URL-encoded title
    book = books[books['Book-Title'] == title]

    if book.empty:
        return "Book not found", 404

    book_info = book.iloc[0]
    isbn = list(map(str, book['ISBN']))
    print(isbn)

    r1 = reviews[reviews['ISBN'].isin(isbn)]['Review'].tolist()
    r2 = reviews[reviews['ISBN'].isin(isbn)]['Rating'].mean()
    print(r1,r2)


    return render_template("book_detail.html", book=book_info, r1=r1, r2=r2)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    isbn = request.form['isbn']
    review = request.form['review']
    rating = int(request.form['rating'])

    # Append new review to the global DataFrame
    global reviews
    new_entry = pd.DataFrame([[isbn, review, rating]], columns=['ISBN', 'Review', 'Rating'])
    reviews = pd.concat([reviews, new_entry], ignore_index=True)

    # Save back to CSV
    reviews.to_csv(REVIEWS_CSV, index=False)

    # Get the book title from the books DataFrame
    title_row = books[books['ISBN'] == isbn]
    if title_row.empty:
        return "Book not found", 404

    book_title = title_row.iloc[0]['Book-Title']
    return redirect(url_for('book_detail', title=book_title))



if __name__ == '__main__':
    app.run(debug=True)

