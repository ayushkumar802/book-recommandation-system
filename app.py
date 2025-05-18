from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np
import urllib.parse



top50= pickle.load(open("top_50.pkl","rb"))

app = Flask(__name__)
# def trim_to_50_words(text):
#     words=  text.split()
#     return ' '.join(words[:5])
# book_name=[]
# for i in list(top50['Book-Title'].values):
#     book_name.append(trim_to_50_words(i))


pt=pickle.load(open("pt.pkl",'rb'))
books=pickle.load(open("books.pkl",'rb'))
similarity=pickle.load(open("similarity.pkl",'rb'))
print(top50.columns)


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
    return render_template('recommend.html', book_list=list(top50['Book-Title'].unique()))

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    if user_input not in pt.index:
        # Handle invalid book input gracefully
        return render_template('recommend.html', data=0, book_list=list(top50['Book-Title'].unique()))

    index = np.where(pt.index == user_input)[0][0]
    similarity_scores = list(enumerate(similarity[index]))
    sorted_books = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:23]  # top 5

    recommendations = []
    for i in sorted_books:
        book_title = pt.index[i[0]]
        book_data = books[books['Book-Title'] == book_title].drop_duplicates('Book-Title')

        if not book_data.empty:
            title = book_data['Book-Title'].values[0]
            author = book_data['Book-Author'].values[0]
            image_url = book_data['Image-URL-M'].values[0]
            recommendations.append([title, author, image_url])

    return render_template('recommend.html', data=recommendations, book_list=list(top50['Book-Title'].unique()))



@app.route('/book/<path:title>')
def book_detail(title):
    title = urllib.parse.unquote(title)  # Decode URL-encoded title
    book = books[books['Book-Title'] == title]

    if book.empty:
        return "Book not found", 404

    book_info = book.iloc[0]
    return render_template("book_detail.html", book=book_info)

if __name__ == '__main__':
    app.run(debug=True)

