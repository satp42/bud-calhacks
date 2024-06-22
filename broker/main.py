from fastapi import FastAPI
import requests, json

import os

from groq import Groq

app = FastAPI()

SYSTEM_PROMPT = """
You are a helpful and proactive assistant. You are able to periodically alert the user to important information.
            
  You receive formation tagged with "Context:" followed by information that may or may not matter to the user.
  You receive periodic updates from multiple sources of information some of which are automated. This may result
  in repeated information. Repetition of information need not be reported to the user.
            
  You are then asked periodically whether or not there is anything interesting to tell the user. Do not include
  anything that the user is likely to know apriori, for example, the user likely already knows where they are or
  what time it is.

  The user may occationally message you directly. You do your best to answer their questions.

  You draw connections between different pieces of contextual information, making connections with previous pieces
  of information and making suggests based on context.
"""

USER_PROMPT = """
I am a student applying to college who is very interested in going to Dartmouth College. 

I am also interested in the field of AI and am a startup founder. 

I am interested in events in my local area.
I am a startup founder who needs to constantly stay updated about research involving language models. 
Let me know if there are any papers relevant to my interests uploaded to Arxiv. If they are not relevant, please ignore the papers.
I like to stay healthy and analyze my health stats weekly. I generally enjoy lifting, crossfit, running, and biking, and plan my workouts based on the weather.

I have the following friends:
- Abhishek also an AI startup founder who is interested in reading papers and attending conferences.
- Manny Miller is an AI Researcher

I like coffee and finding different places to explore and work from. I am also interested in finding new places to eat.
"""

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.get("/")
def read_root():
    # r = requests.get("https://oauth.reddit.com/.json").json()
    # print(r)
    # print(r["data"]["children"][0]["data"]["title"])

    posts = []
    f = open("example.json" )
    data = json.load(f)
    for i in data["data"]["children"]:
        if i["data"]["clicked"]:
            continue

        post = {
            "author": i["data"]["author"], # author name
            "author_flair_text": i["data"]["author_flair_text"], # author flair text
            "clicked": i["data"]["clicked"], # has the user clicked on the post
            "created_utc": i["data"]["created_utc"], # post time
            "domain": i["data"]["domain"], # domain of the post
            "title": i["data"]["title"], # post title
            "permalink": "https://www.reddit.com" + i["data"]["permalink"], # link to the post
            "url": i["data"]["url"], # link to the post
            "subreddit": i["data"]["subreddit"], # subreddit name
            "locked": i["data"]["locked"], # comments locked
            "over_18": i["data"]["over_18"], # NSFW
            "is_self": i["data"]["is_self"], # is a text post
            "selftext": i["data"]["selftext"], # post text
            "score": i["data"]["score"], # post score
            "num_comments": i["data"]["num_comments"], # number of comments
            "num_crossposts": i["data"]["num_crossposts"], # number of crossposts
            "upvote_ratio": i["data"]["upvote_ratio"], # upvote ratio
            "upvotes": i["data"]["ups"], # number of upvotes
            "downvotes": i["data"]["downs"], # number of downvotes
            "gilded": i["data"]["gilded"], # number of gilds
            "saved": i["data"]["saved"], # saved by the user
            "spoiler": i["data"]["spoiler"], # spoiler
            "view_count": i["data"]["view_count"], # view count (if video, else null)
        }
        posts.append(post)

    
    output = "User's Reddit Feed (provide links if important):"


    for post in posts:
        # Only include text posts
        if not post["is_self"]:
            continue
        output = output + "\nTitle: " + post["title"]
        output = output + "\nSubreddit: " + post["subreddit"]
        output = output + "\nContent: " + post["selftext"]
        output = output + "\nLink: " + post["permalink"]

    print(output)
    
    chat_completion = client.chat.completions.create(
        
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": "The user has prodvided the following information about him or herself: \n\n{}".format(USER_PROMPT),
            },
            {
                # Selects posts from Reddit that are relevant to the user given the prompt. This message provides the LLM with the reddit posts.
                "role": "user",
                "content": "If there is anything important, tell the user in a friendly tone with modest elaboration. Write with professionalism and brevity, limiting your responses to one or two sentences (IN TOTAL). If you reference a post, provide the link. If there is no new information, simply type 'None'. \n\n{}".format(output),
            }
        ],
        model="llama3-8b-8192",
    )

    print(chat_completion.choices)


    return {"response": chat_completion.choices[0].message.content}
