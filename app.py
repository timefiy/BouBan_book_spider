from flask import Flask
import views

app = Flask(__name__)


# ==================== 页面路由 ====================
@app.route('/')
def index():
    return views.index()

@app.route('/authors-analysis')
def authors_analysis_page():
    return views.authors_analysis_page()

@app.route('/comments-analysis')
def comments_analysis_page():
    return views.comments_analysis_page()

@app.route('/time-analysis')
def time_analysis_page():
    return views.time_analysis_page()

@app.route('/length-analysis')
def length_analysis_page():
    return views.length_analysis_page()


# ==================== API路由 ====================
@app.route('/api/authors-by-country')
def authors_by_country():
    return views.authors_by_country()

@app.route('/api/comment-usefulness')
def comment_usefulness():
    return views.comment_usefulness()

@app.route('/api/comment-time-analysis')
def comment_time_analysis():
    return views.comment_time_analysis()

@app.route('/api/book-length-preference')
def book_length_preference():
    return views.book_length_preference()


if __name__ == '__main__':
    app.run(debug=True)
