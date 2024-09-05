# SentimentIQ
Whether you're interested in tracking public opinions about emerging trends, or understanding customer feedback on a product, SentimentIQ gives you the tools to analyze sentiment data efficiently and visually.

Using a combination of VADER Sentiment Analysis and the Reddit API (PRAW), SentimentIQ delivers an easy-to-use interface where users can search for subreddits, select post types, and instantly get a breakdown of the sentiment in the comments, displayed in an interactive pie chart.



**Demo:** 

https://github.com/user-attachments/assets/c594e41b-fd19-4c2a-9140-1535947ae689

**Set-Up Instructions**

- Clone the repository
- Install dependencies: Make sure you have Python installed, then run: `pip install -r requirements.txt`
- Set up Reddit API credentials: Visit Reddit's developer portal and create a new application. Add your credentials (client ID, client secret, and user agent) to app.py 
- Run the Flask app: `python app.py`
- Access the app: Open your browser and navigate to http://localhost:8000. Log in to Reddit and start analyzing comments by entering a subreddit name.
