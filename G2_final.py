import requests
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

url = "https://data.g2.com/api/v1/survey-responses"
analyzer = SentimentIntensityAnalyzer()


params = {
    "filters[product_name]": "G2 Marketing Solutions", #user can input as well, what kind of product do they need
    "page[size]": 10
}


headers = {
    "Authorization": "Bearer 7105c53f412b2be486128b5acca018ea55165378228e03fadbe523dbe9550712",
    "Content-Type": "application/vnd.api+json"
}


#extract relevant feature sets
def preprocess_and_extract_features(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
  #aspect keywords-----> user related
    aspect_keywords = {
    "application_performance": ["performance", "speed", "response time", "efficiency", "lag", "latency", "loading time", "optimization"],
    "user_experience": ["user experience", "usability", "interface", "navigation", "intuitive", "visibility", "layout", "design", "smoothness", "accessibility"],
    "missing_functionality": ["missing", "lacking", "absent", "unavailable", "need", "require", "wish", "should have", "not have", "not include", "limited", "incomplete", "unmet needs", "desired features"],
    "bugs": ["bug", "issue", "error", "crash", "glitch", "malfunction", "problem", "flaw", "defect"]
}

    
   
    tokens = word_tokenize(text.lower())
    filtered_tokens = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum() and token not in stop_words]
    
    # Extraction
    relevant_features = []
    for token in filtered_tokens:
        for aspect, keywords in aspect_keywords.items():
            if any(keyword in token for keyword in keywords):
                relevant_features.append(aspect)
    
    return relevant_features


def filter_comments_by_aspect(reviews, aspect_key):
    filtered_comments = []
    for review in reviews:
        comment_ans = review['attributes']['comment_answers']
        if comment_ans:
            for key, value in comment_ans.items():
                features = preprocess_and_extract_features(value['value'])
                if aspect_key in features:
                    filtered_comments.append((product_name, value['value']))
    return filtered_comments


response = requests.get(url, params=params, headers=headers)


if response.status_code == 200: #successful requests
    
    data = response.json()
    
    
    reviews = data['data']
    votes_up_list=[]
    votes_down_list=[]
    star_ratings=[]
    
    feature_sets = []
    for review in reviews:  
        product_name = review['attributes']['product_name']
        review_title = review['attributes']['title']    
        star_rating = review['attributes']['star_rating']
        is_public = review['attributes']['is_public']
        is_bp = review['attributes']['is_business_partner']
        review_source = review['attributes']['review_source']
        comment_ans = review['attributes']['comment_answers'] 
        sec_comment = review['attributes']['secondary_answers']
        country_name=review['attributes']['country_name']
        votes_up=review['attributes']['votes_up']
        votes_down=review['attributes']['votes_down']
        
        
        
        print("Product Name:", product_name)
        print("Country Name:", country_name)
        print("Review Title:", review_title)
        print("Star Rating:", star_rating)
        print("Votes Up",votes_up)
        print("Votes Down",votes_down)
        
        if comment_ans:
            print("Comment Answers: ")
            for key, value in comment_ans.items():
                print(f"{key}----> {value['value']}")
                features = preprocess_and_extract_features(value['value'])
                feature_sets.extend(features)
                text = value["value"]
                    #print("Comment:", text)
                sentiment_score = analyzer.polarity_scores(text)
                print("Sentiment Score for COMMENT:", sentiment_score)
                
                # if key == 'benefits':
                #     benefits_comment = value['value']
                #     bene_features = preprocess_and_extract_features(benefits_comment)
                #     feature_sets.extend(bene_features)
           
                    
            
        # if comment_ans:
        #     print("Comment Answers: ")
        #     for key, value in comment_ans.items():
        #         print(f"{key}----> {value['value']}")
        #         features = preprocess_and_extract_features(value['value'])
        #         feature_sets.extend(features)
        
        
        if sec_comment:
            print("--------------SECONDARY COMMENTS------------------")
            c=0
            tot=0
            print("Secondary Comments:")
            for key, value in sec_comment.items():
                #print(f"{value['text']}----> {value['value']}")
                c=c+1
                tot=tot+value['value']
            if (tot/c)>5:
                print("The average scores for"+ product_name +"is better")
                print(f"{value['text']}----> {value['value']}")
                
            print("average_score",tot/c)
        
        print("Star Rating:", star_rating)        
        print("-----------------------------------------------------------------------------------------")
    
        votes_up_list.append(votes_up)
        votes_down_list.append(votes_down)
        star_ratings.append(star_rating)
        
        
        
        

    
    fig, ax = plt.subplots()
    bar_width = 0.35
    index = range(len(reviews))
    ax.bar(index, votes_up_list, bar_width, label='Votes Up', color='b')
    ax.bar([i + bar_width for i in index], votes_down_list, bar_width, label='Votes Down', color='r')
    
    ax.set_xlabel('Reviews')
    ax.set_ylabel('Number of Votes')
    ax.set_title('Votes Up vs Votes Down for Each Review')
    ax.set_xticks([i + bar_width/2 for i in index])
    ax.set_xticklabels([f"Review {i+1}" for i in range(len(reviews))])
    ax.legend()
    ax2 = ax.twinx()
    ax2.plot(index, star_ratings, color='g', marker='o', linestyle='-', linewidth=2, label='Star Rating')
    ax2.set_ylabel('Star Rating')
    ax2.legend(loc='upper right')

    plt.show()
    plt.show()

   

       
       
   
    feature_sets_count = Counter(feature_sets)

    # Print the most common feature sets
    ##FILTER-->WHAT THE CUSTOMER IS LOOKING?
    # country_name=input("Please Enter the country Name")
    # rev_src=input("Please enter Review Source(Organic/Not Organic)")
    print("Top feature sets that customers are looking for:")
    for feature_set, count in feature_sets_count.most_common():
        print(f"{feature_set}: {count} mentions")
    

    
    aspect_key = input("Enter an aspect key (e.g., application_performance, user_experience, etc.): ")

    # Filter comments based on the aspect key
    filtered_comments = filter_comments_by_aspect(reviews, aspect_key)

    
    if filtered_comments:
        print(f"Comments related to the aspect '{aspect_key}':")
        for product, comment in filtered_comments:
            print(f"Product: {product} - Comment: {comment}")
    else:
        print("Products with specific requirements not found")
   
    
        
else:
    print("Failed to fetch data:", response.status_code)
