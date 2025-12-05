# logic_planner/resources.py
import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Expanded curated resources database
resources = {
    # Machine Learning Topics
    "Linear Regression": [
        {"type": "concept", "title": "StatQuest – Linear Regression", "url": "https://youtu.be/nk2CQITm_eo"},
        {"type": "practice", "title": "Kaggle: Linear Regression Exercises", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
        {"type": "read", "title": "sklearn: Linear Models", "url": "https://scikit-learn.org/stable/modules/linear_model.html"}
    ],
    "Decision Trees": [
        {"type": "concept", "title": "Entropy & Information Gain (video)", "url": "https://youtu.be/IO5l86Z5O3g"},
        {"type": "practice", "title": "Hands-on Decision Trees (Python)", "url": "https://www.datacamp.com/tutorial/decision-tree-classification-python"},
        {"type": "read", "title": "sklearn: Decision Trees", "url": "https://scikit-learn.org/stable/modules/tree.html"}
    ],
    "Neural Networks": [
        {"type": "concept", "title": "3Blue1Brown – Neural Nets", "url": "https://youtu.be/aircAruvnKk"},
        {"type": "practice", "title": "Build a Simple NN (PyTorch)", "url": "https://pytorch.org/tutorials/beginner/basics/intro.html"},
        {"type": "read", "title": "CS231n Notes – Backprop", "url": "https://cs231n.github.io/optimization-2/"}
    ],
    "Support Vector Machines": [
        {"type": "concept", "title": "SVM Intuition (video)", "url": "https://youtu.be/efR1C6CvhmE"},
        {"type": "practice", "title": "SVM in Python (guide)", "url": "https://scikit-learn.org/stable/auto_examples/svm/plot_iris_svc.html"},
        {"type": "read", "title": "Kernel Tricks Explained", "url": "https://data-science-blog.com/blog/2017/08/29/kernel-trick-explained/"}
    ],
    "Clustering (K-Means)": [
        {"type": "concept", "title": "K-Means Explained (video)", "url": "https://youtu.be/4b5d3muPQmA"},
        {"type": "practice", "title": "K-Means with sklearn", "url": "https://scikit-learn.org/stable/modules/clustering.html#k-means"},
        {"type": "read", "title": "Choosing K (Elbow/Silhouette)", "url": "https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation"}
    ],
    "Principal Component Analysis": [
        {"type": "concept", "title": "PCA Explained (video)", "url": "https://youtu.be/FgakZw6K1QQ"},
        {"type": "practice", "title": "PCA in Python (sklearn)", "url": "https://scikit-learn.org/stable/modules/decomposition.html#pca"},
        {"type": "read", "title": "Understanding PCA", "url": "https://towardsdatascience.com/a-one-stop-shop-for-principal-component-analysis-5582fb7e0a9c"}
    ],
    "Random Forests": [
        {"type": "concept", "title": "Random Forest Intuition (video)", "url": "https://youtu.be/J4Wdy0Wc_xQ"},
        {"type": "practice", "title": "Random Forest in Python (sklearn)", "url": "https://scikit-learn.org/stable/modules/ensemble.html#random-forests"},
        {"type": "read", "title": "Comprehensive Guide to Random Forests", "url": "https://towardsdatascience.com/random-forest-in-python-24d0893d51c0"}
    ],
    
    # Mathematics Topics
    "Algebra": [
        {"type": "concept", "title": "Khan Academy - Algebra", "url": "https://www.khanacademy.org/math/algebra"},
        {"type": "practice", "title": "IXL Algebra Practice", "url": "https://www.ixl.com/math/algebra-1"},
        {"type": "read", "title": "Algebra Basics", "url": "https://www.mathsisfun.com/algebra/"}
    ],
    "Calculus": [
        {"type": "concept", "title": "3Blue1Brown - Essence of Calculus", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr"},
        {"type": "practice", "title": "Paul's Online Calculus Notes", "url": "https://tutorial.math.lamar.edu/Classes/CalcI/CalcI.aspx"},
        {"type": "read", "title": "Khan Academy - Calculus", "url": "https://www.khanacademy.org/math/calculus-1"}
    ],
    "Statistics": [
        {"type": "concept", "title": "StatQuest - Statistics Fundamentals", "url": "https://www.youtube.com/playlist?list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9"},
        {"type": "practice", "title": "Statistics Practice Problems", "url": "https://www.khanacademy.org/math/statistics-probability"},
        {"type": "read", "title": "Statistics How To", "url": "https://www.statisticshowto.com/"}
    ],
    
    # Programming Topics
    "Python": [
        {"type": "concept", "title": "Python for Beginners", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"},
        {"type": "practice", "title": "Python Exercises", "url": "https://www.w3schools.com/python/python_exercises.asp"},
        {"type": "read", "title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/"}
    ],
    "Data Structures": [
        {"type": "concept", "title": "Data Structures Explained", "url": "https://www.youtube.com/watch?v=RBSGKlAvoiM"},
        {"type": "practice", "title": "LeetCode Data Structures", "url": "https://leetcode.com/problemset/all/?topicSlugs=array"},
        {"type": "read", "title": "GeeksforGeeks DS Guide", "url": "https://www.geeksforgeeks.org/data-structures/"}
    ],
    "Algorithms": [
        {"type": "concept", "title": "Algorithms Visualization", "url": "https://visualgo.net/en"},
        {"type": "practice", "title": "HackerRank Algorithms", "url": "https://www.hackerrank.com/domains/algorithms"},
        {"type": "read", "title": "Algorithm Design Manual", "url": "https://www.algorist.com/"}
    ]
}

# Generic fallback resources by category
fallback_resources = {
    "concept": [
        {"type": "concept", "title": "Khan Academy - {topic}", "url": "https://www.khanacademy.org/search?search_again=1&page_search_query={topic}"},
        {"type": "concept", "title": "Coursera - {topic}", "url": "https://www.coursera.org/search?query={topic}"},
    ],
    "practice": [
        {"type": "practice", "title": "Practice on Brilliant", "url": "https://brilliant.org/courses/"},
        {"type": "practice", "title": "Exercises on W3Schools", "url": "https://www.w3schools.com/"},
    ],
    "read": [
        {"type": "read", "title": "Wikipedia - {topic}", "url": "https://en.wikipedia.org/wiki/{topic}"},
        {"type": "read", "title": "GeeksforGeeks - {topic}", "url": "https://www.geeksforgeeks.org/?s={topic}"},
    ]
}


def create_session_with_timeout(timeout=3, max_retries=1):
    """
    Create a requests session with timeout and retry configuration.
    This prevents hanging requests.
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_youtube_videos(query, api_key, max_results=2, timeout=3):
    """
    Fetch YouTube videos for a given query with strict timeout.
    Returns list of video resources.
    """
    print(f"🔍 Attempting to fetch YouTube videos for: {query}")
    
    if not api_key:
        print("⚠️ No YouTube API key provided")
        return []
    
    try:
        print(f"📡 Making YouTube API request (timeout: {timeout}s)...")
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": api_key,
            "relevanceLanguage": "en",
            "safeSearch": "strict"
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        print(f"✅ YouTube API responded with status: {response.status_code}")
        
        if response.status_code == 200:
            items = response.json().get("items", [])
            print(f"📹 Found {len(items)} videos")
            return [
                {
                    "title": video["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                    "type": "video"
                }
                for video in items
            ]
        elif response.status_code == 403:
            print(f"❌ YouTube API quota exceeded or invalid key")
            return []
        else:
            print(f"⚠️ YouTube API returned status code: {response.status_code}")
            return []
            
    except requests.exceptions.Timeout:
        print(f"⏱️ YouTube API request timed out after {timeout}s")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ YouTube API request error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching YouTube videos: {e}")
        return []
    finally:
        # Ensure session is closed
        try:
            session.close()
        except:
            pass


def get_fallback_resources_for_topic(topic, subject="General"):
    """
    Get immediate fallback resources without any API calls.
    This ensures we always have something to show.
    """
    fallback_list = []
    
    # Add one resource from each category
    for category in ["concept", "practice", "read"]:
        for fallback in fallback_resources.get(category, []):
            fallback_resource = {
                "type": fallback["type"],
                "title": fallback["title"].replace("{topic}", topic),
                "url": fallback["url"].replace("{topic}", topic.replace(" ", "+"))
            }
            fallback_list.append(fallback_resource)
            break  # Only take one from each category
    
    # Add subject-specific search if provided
    if subject != "General":
        fallback_list.append({
            "type": "video",
            "title": f"YouTube: {subject} - {topic}",
            "url": f"https://www.youtube.com/results?search_query={subject}+{topic}".replace(" ", "+")
        })
    
    return fallback_list


def fetch_resources_with_fallback(topic, subject="General", youtube_api_key=None, max_youtube_timeout=3):
    """
    Fetch learning resources with multiple sources and fallback mechanisms.
    OPTIMIZED: Returns immediately if curated resources exist, only tries YouTube if needed.
    
    Priority:
    1. Curated local resources (if available) - INSTANT
    2. YouTube API (with strict timeout) - if key provided and curated not available
    3. Generic educational platform resources - INSTANT FALLBACK
    
    Args:
        topic: The topic to fetch resources for
        subject: The subject category (for context)
        youtube_api_key: Optional YouTube API key
        max_youtube_timeout: Maximum seconds to wait for YouTube API (default: 3)
    
    Returns:
        List of resource dictionaries with title, url, and type
    """
    collected_resources = []
    
    # 1. Check curated resources first (highest quality, INSTANT)
    if topic in resources:
        collected_resources.extend(resources[topic])
        # If we have curated resources, return immediately without trying YouTube
        return collected_resources[:5]
    
    # 2. Only try YouTube API if:
    #    - We have an API key
    #    - We don't have enough curated resources
    if youtube_api_key and len(collected_resources) < 2:
        try:
            search_query = f"{subject} {topic} tutorial" if subject != "General" else f"{topic} tutorial"
            youtube_videos = fetch_youtube_videos(
                search_query, 
                youtube_api_key, 
                max_results=2,  # Only get 2 videos max
                timeout=max_youtube_timeout
            )
            
            if youtube_videos:
                collected_resources.extend(youtube_videos)
                
        except Exception as e:
            print(f"YouTube fetch completely failed for {topic}: {e}")
            # Continue to fallback resources
    
    # 3. Add generic fallback resources
    fallback_list = get_fallback_resources_for_topic(topic, subject)
    collected_resources.extend(fallback_list)
    
    # 4. Emergency fallback - if still empty
    if not collected_resources:
        collected_resources = [
            {
                "type": "read",
                "title": f"Search Google for {topic}",
                "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}"
            },
            {
                "type": "concept",
                "title": f"YouTube search for {topic}",
                "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
            },
            {
                "type": "practice",
                "title": f"Khan Academy - {topic}",
                "url": f"https://www.khanacademy.org/search?search_again=1&page_search_query={topic.replace(' ', '+')}"
            }
        ]
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_resources = []
    for resource in collected_resources:
        if resource["url"] not in seen_urls:
            seen_urls.add(resource["url"])
            unique_resources.append(resource)
    
    return unique_resources[:5]  # Return max 5 resources