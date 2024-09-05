from flask import Flask, redirect, request, render_template
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from prawcore import NotFound, Forbidden, ServerError

app = Flask(__name__)

# Set up your Reddit API credentials here
reddit = praw.Reddit(
    # client_id='xxxxxxxxxxxxxxxxxxxxxxxxxx',
    # client_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxx',
    # user_agent='SentimentIQ by /u/xxxxxxxxxxxxxxxxxx',
    # redirect_uri='http://localhost:8000/callback'
)

# Initialize VADER for sentiment analysis
analyzer = SentimentIntensityAnalyzer()

# Home route with Reddit authentication link
@app.route('/')
def homepage():
    auth_url = reddit.auth.url(['identity', 'read'], 'random_state', 'permanent')
    return f'<a href="{auth_url}">Login with Reddit</a>'

# Callback route after Reddit login
@app.route('/callback')
def callback():
    code = request.args.get('code')
    reddit.auth.authorize(code)
    return redirect('/analyze_comments')

# Function to analyze sentiment of comments
def analyze_sentiment(text):
    sentiment = analyzer.polarity_scores(text)
    return sentiment

@app.route('/analyze_comments', methods=['GET'])
def analyze_comments():
    # Get the subreddit and post type from user input
    subreddit_name = request.args.get('subreddit', None)
    post_type = request.args.get('post_type', 'top')  # Default to 'top'

    if not subreddit_name:
        return render_template('index.html', results=None, avg_sentiment=None, error="Subreddit name is required.")

    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Fetch posts based on post type
        if post_type == 'new':
            posts = subreddit.new(limit=10)
        elif post_type == 'hot':
            posts = subreddit.hot(limit=10)
        elif post_type == 'rising':
            posts = subreddit.rising(limit=10)
        else:  # Default to 'top'
            posts = subreddit.top(limit=10)

        sentiment_results = []
        total_sentiment = {'pos': 0, 'neg': 0, 'neu': 0, 'compound': 0}
        comment_count = 0

        for post in posts:
            post.comments.replace_more(limit=None)
            for comment in post.comments.list():
                sentiment = analyze_sentiment(comment.body)
                sentiment_results.append({
                    'comment': comment.body,
                    'sentiment': sentiment
                })

                # Accumulate sentiment scores
                total_sentiment['pos'] += sentiment['pos']
                total_sentiment['neg'] += sentiment['neg']
                total_sentiment['neu'] += sentiment['neu']
                total_sentiment['compound'] += sentiment['compound']
                comment_count += 1

        # Calculate average sentiment scores and convert to percentages
        if comment_count > 0:
            avg_sentiment = {
                'pos': (total_sentiment['pos'] / comment_count) * 100,
                'neg': (total_sentiment['neg'] / comment_count) * 100,
                'neu': (total_sentiment['neu'] / comment_count) * 100,
                'compound': (total_sentiment['compound'] / comment_count) * 100
            }
        else:
            avg_sentiment = {'pos': 0, 'neg': 0, 'neu': 0, 'compound': 0}

        # Format the percentages to one decimal place
        avg_sentiment = {k: f"{v:.1f}%" for k, v in avg_sentiment.items()}

        return render_template('index.html', results=sentiment_results, avg_sentiment=avg_sentiment, subreddit=subreddit_name, error=None)

    except NotFound:
        error_message = f"Error: The subreddit '{subreddit_name}' was not found. Please check the name and try again."
        return render_template('index.html', error=error_message, results=None, avg_sentiment=None)

    except Forbidden:
        error_message = f"Error: The subreddit '{subreddit_name}' is private and cannot be accessed."
        return render_template('index.html', error=error_message, results=None, avg_sentiment=None)

    except ServerError as e:
        error_message = "Error: Reddit servers are currently unavailable. Please try again later."
        print(f"Server error: {e}")  # You can also use logging here.
        return render_template('index.html', error=error_message, results=None, avg_sentiment=None)

    except Exception as e:
        error_message = f"An unexpected error occurred. Please try again later."
        print(f"Unexpected error: {e}")  # Log the error for debugging
        return render_template('index.html', error=error_message, results=None, avg_sentiment=None)


if __name__ == "__main__":
    app.run(port=8000)
