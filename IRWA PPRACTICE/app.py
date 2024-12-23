import streamlit as st
import pickle
import requests
import pandas as pd

# Load movie data and similarity values
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity_value = pickle.load(open("similarity_value.pkl", 'rb'))
movies_list = movies['title'].values

# Load the user-movie matrix and user similarity DataFrame from the pickle file
with open('user_movie_recommendation.pkl', 'rb') as f:
    user_movie_matrix, user_similarity_df = pickle.load(f)

# Function to fetch the poster using TMDb API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=()&language=en-US"
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path')
    if poster_path:  # Check if a poster is available
        full_path = "https://image.tmdb.org/t/p/w500" + poster_path
        return full_path
    else:
        return "No poster available"  # Handle case where no poster is found

st.sidebar.title("Navigation")
nav_option = st.sidebar.radio("Go to", ("Home", "Account Details", "Browser History", "Sign Out"))

if nav_option == "Home":
    st.header("Movie Recommender System")

    # Add a search bar at the top of the home page
    search_term = st.text_input("Search for a movie:", "")
    
    # Load merged_df from pickle
    with open('merged_df.pkl', 'rb') as f:
        merged_df = pickle.load(f)

    # Initialize a variable to hold the selected movie ID for the banner display
    selected_movie_id = None

    # Filter movies based on the search term
    if search_term:
        filtered_movies = merged_df[merged_df['title'].str.contains(search_term, case=False, na=False)]
        filtered_movie_titles = filtered_movies['title'].tolist()
        
        st.write("Search Results:")
        if not filtered_movie_titles:
            st.write("No movies found.")
        else:
            # Display movie titles with a button to view details
            for title in filtered_movie_titles:
                movie_id = filtered_movies[filtered_movies['title'] == title]['movie_id'].values[0]  # Get movie_id
                if st.button(f"View {title}", key=movie_id):  # Create a button for each title
                    selected_movie_id = movie_id  # Store the selected movie ID

    else:
        st.write("Please enter a search term to see results.")  # Prompt the user to enter a search term

    # Display the banner for the selected movie
    if selected_movie_id:
        poster_url = fetch_poster(selected_movie_id)  # Fetch the poster using the selected movie ID
        st.image(poster_url, use_column_width=True)  # Display the poster image

    # Initialize recommended_titles and recommended_ids
    recommended_titles = []
    recommended_ids = []

    # Define the recommend_movies_collaborative function
    def recommend_movies_collaborative(user_id, num_recommendations=5):
        # Get the similarity scores for the target user
        similar_users = user_similarity_df[user_id].sort_values(ascending=False)

        # Movies the user has already watched
        user_watched_movies = user_movie_matrix.loc[user_id].dropna().index.tolist()

        # Initialize an empty Series to store movie recommendations
        recommended_movies = pd.Series(dtype=float)

        # Loop through similar users to gather movies they rated highly
        for similar_user_id in similar_users.index[1:]:
            similar_user_ratings = user_movie_matrix.loc[similar_user_id].dropna()

            # Filter out movies the target user has already watched
            new_movies = similar_user_ratings[~similar_user_ratings.index.isin(user_watched_movies)]

            # Add these movies to the recommendation list
            recommended_movies = pd.concat([recommended_movies, new_movies])

            # Stop if we've gathered enough recommendations
            if len(recommended_movies) >= num_recommendations:
                break

        # Get the top N recommended movie IDs
        if not recommended_movies.empty:
            recommended_movie_ids = recommended_movies.sort_values(ascending=False).head(num_recommendations).index.tolist()

            # Map the movie IDs to their titles
            recommended_movie_titles = merged_df.loc[merged_df['movie_id'].isin(recommended_movie_ids), 'title'].unique()
            return recommended_movie_titles, recommended_movie_ids  # Return both titles and IDs
        else:
            return [], []  # Return empty lists if no recommendations were found

    # Get user input for user ID
    user_id_input = st.number_input("Enter User ID:", min_value=1, step=1)

    if st.button("Recommend Movies"):
        recommended_titles, recommended_ids = recommend_movies_collaborative(user_id=user_id_input, num_recommendations=5)

        # Check if recommended_titles is empty
        if len(recommended_titles) > 0:
            st.write("Recommended movie titles for User", user_id_input, ":")
            for title in recommended_titles:
                st.write(title)
        else:
            st.write("No recommendations found.")

    # Display banners for recommended movies
    if recommended_ids:  # Check if recommended_ids has been populated
        st.write("Movie Posters:")
        cols = st.columns(len(recommended_ids))
        
        for col, movie_id in zip(cols, recommended_ids):
            poster_url = fetch_poster(movie_id)  # Fetch the poster URL using the movie ID
            with col:
                st.image(poster_url, use_column_width=True)  # Display the poster image

    select_value = st.selectbox("Select movie from dropdown", movies_list)

    # Recommend movies based on similarity
    def recommend(movie):
        index = movies[movies['title'] == movie].index[0]
        distance = sorted(list(enumerate(similarity_value[index])), reverse=True, key=lambda vector: vector[1])
        recommend_movie = []
        recommend_poster = []

        for i in distance[1:6]:  # Loop through the top 5 recommended movies
            movie_id = movies.iloc[i[0]].movie_id  # Access the movie ID correctly from DataFrame
            recommend_movie.append(movies.iloc[i[0]].title)  # Access the title correctly
            recommend_poster.append(fetch_poster(movie_id))  # Fetch poster using the correct movie ID
        return recommend_movie, recommend_poster

    if st.button("Show Recommend"):
        movie_name, movie_poster = recommend(select_value)

        # Ensure there are at least 5 recommendations to avoid index errors
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, col in enumerate([col1, col2, col3, col4, col5]):
            if i < len(movie_name):  # Check if the index is within the list range
                with col:
                    st.text(movie_name[i])
                    st.image(movie_poster[i])  # Display the poster for each recommended movie
            else:
                with col:
                    st.text("No Recommendation")  #  handle cases with fewer recommendations

elif nav_option == "Account Details":
    st.header("Account Details")
    st.write("User account information goes here.")
    #  can add more details or even an input form for user account updates

elif nav_option == "Browser History":
    st.header("Browser History")
    st.write("Here you can display the user's browsing history.")
    #  can implement functionality to display browsing history

elif nav_option == "Sign Out":
    st.header("Sign Out")
    st.write("You have signed out successfully.")
    # Add logic for sign out functionality if needed
