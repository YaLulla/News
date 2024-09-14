import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.blocking import BlockingScheduler

# Replace 'YOUR_BOT_TOKEN' and 'YOUR_CHANNEL_ID' with your actual bot token and channel ID
BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_ID = '@your_channel_id'  # Use the channel username with '@' or the numeric ID

bot = Bot(token=BOT_TOKEN)

def get_news_from_site(url, headline_tag, summary_tag, image_tag, video_tag):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('article')  # Adjust the tag based on the website structure
    news_items = []

    for article in articles:
        headline = article.find(headline_tag).get_text()  # Adjust the tag based on the website structure
        summary = article.find(summary_tag).get_text() if article.find(summary_tag) else article.find('blog').get_text()  # Use blog if summary not found
        image_url = article.find(image_tag)['src'] if article.find(image_tag) else None
        video_url = article.find(video_tag)['src'] if article.find(video_tag) else None
        news_items.append({'headline': headline, 'summary': summary, 'image_url': image_url, 'video_url': video_url})

    return news_items

def get_news():
    news_sites = [
        {'url': 'https://example1.com/bengali-news', 'headline_tag': 'h2', 'summary_tag': 'p', 'image_tag': 'img', 'video_tag': 'video'},
        {'url': 'https://example2.com/bengali-news', 'headline_tag': 'h3', 'summary_tag': 'p', 'image_tag': 'img', 'video_tag': 'video'},
        # Add more sites as needed
    ]
    all_news = []
    for site in news_sites:
        news_items = get_news_from_site(site['url'], site['headline_tag'], site['summary_tag'], site['image_tag'], site['video_tag'])
        all_news.extend(news_items)
    return all_news

def start(update, context):
    update.message.reply_text('Welcome! I will send you the latest Bengali news.')

def send_news(update, context):
    news_items = get_news()
    for item in news_items:
        caption = f"{item['headline']}\n\n{item['summary']}\n\n#BengalBulletin"
        if item['image_url']:
            bot.send_photo(chat_id=update.message.chat_id, photo=item['image_url'], caption=caption)
        elif item['video_url']:
            bot.send_video(chat_id=update.message.chat_id, video=item['video_url'], caption=caption)
        else:
            bot.send_message(chat_id=update.message.chat_id, text=caption)

def post_news_to_channel():
    news_items = get_news()
    for item in news_items:
        caption = f"{item['headline']}\n\n{item['summary']}\n\n#BengalBulletin"
        if item['image_url']:
            bot.send_photo(chat_id=CHANNEL_ID, photo=item['image_url'], caption=caption)
        elif item['video_url']:
            bot.send_video(chat_id=CHANNEL_ID, video=item['video_url'], caption=caption)
        else:
            bot.send_message(chat_id=CHANNEL_ID, text=caption)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('news', send_news))

    # Schedule automatic news posting
    scheduler = BlockingScheduler()
    scheduler.add_job(post_news_to_channel, 'interval', hours=1)
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
      
