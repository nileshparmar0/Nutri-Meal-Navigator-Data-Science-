import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration with custom theme
st.set_page_config(
    layout="wide",
    page_title="🍲 NutriMeal Navigator",
    initial_sidebar_state="expanded"
)

# Initialize session state for favorites
if 'favorites' not in st.session_state:
    st.session_state.favorites = set()

@st.cache_data
def load_data():
    try:
        data = pd.read_csv('NewPeanut.csv')
        return data
    except FileNotFoundError:
        st.error("CSV file not found. Please check if 'NewPeanut.csv' is in the correct directory.")
        return pd.DataFrame()

def filter_recipes(df, dietary_restrictions, meal_type, rating_range, calories_range):
    if df.empty:
        return df

    filtered_df = df.copy()

    if dietary_restrictions:
        filtered_df = filtered_df[filtered_df[dietary_restrictions].all(axis=1)]

    if meal_type and meal_type != 'Any':
        filtered_df = filtered_df[filtered_df['meal_type'].str.contains(meal_type, case=False, na=False)]

    if calories_range:
        filtered_df = filtered_df[
            (filtered_df['calories'] >= calories_range[0]) & 
            (filtered_df['calories'] <= calories_range[1])
        ]

    if rating_range:
        filtered_df = filtered_df[
            (filtered_df['rating'] >= rating_range[0]) & 
            (filtered_df['rating'] <= rating_range[1])
        ]

    return filtered_df

def plot_meal_distribution(df):
    fig = px.pie(
        df, 
        names='meal_type', 
        title='Meal Type Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=False,
        title_x=0.5,
        title_font_size=20,
        height=400
    )
    return fig

def plot_rating_distribution(df):
    fig = px.histogram(
        df, 
        x='rating',
        title='Rating Distribution',
        nbins=20,
        color_discrete_sequence=['#FF4B4B'],
        opacity=0.7
    )
    fig.update_layout(
        xaxis_title="Rating",
        yaxis_title="Number of Recipes",
        bargap=0.1,
        title_x=0.5,
        title_font_size=20,
        height=400
    )
    return fig

def plot_nutrition_comparison(df):
    avg_nutrition = df[['calories', 'protein', 'fat']].mean()
    fig = go.Figure(data=[
        go.Bar(
            x=avg_nutrition.index,
            y=avg_nutrition.values,
            marker_color=['#FF9B9B', '#FFB4B4', '#FFCECE'],
            text=avg_nutrition.values.round(1),
            textposition='auto',
        )
    ])
    fig.update_layout(
        title={
            'text': "Average Nutritional Content",
            'x': 0.5,
            'font_size': 20
        },
        xaxis_title="Nutrient",
        yaxis_title="Amount (g/serving)",
        height=400,
        showlegend=False
    )
    return fig

def main():
    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    /* Main theme colors and fonts */
    :root {
        --primary-color: #FF4B4B;
        --secondary-color: #FF6B6B;
        --background-color: #FFFFFF;
        --text-color: #333333;
    }

    /* Header styling */
    .main-header {
        font-size: 3.5rem !important;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Subheader styling */
    .subheader {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Card styling */
    .recipe-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .recipe-card:hover {
        transform: translateY(-5px);
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        height: 3em;
        background-color: var(--primary-color);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: var(--secondary-color);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Metric container styling */
    .metric-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 300px;
        max-width: 400px;
        padding: 2rem 1rem;
    }

    /* DataFrame styling */
    .dataframe {
        font-size: 14px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown('<p class="main-header">🍲 NutriMeal Navigator</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Discover recipes tailored to your dietary preferences</p>', unsafe_allow_html=True)

    # Load data
    df = load_data()
    if df.empty:
        st.stop()

    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Recipe Filters")
        
        with st.expander("Dietary Restrictions", expanded=True):
            dietary_restrictions = st.multiselect(
                'Select your dietary preferences',
                ['Vegetarian', 'Vegan', 'Gluten-Free', 'Peanut-Free'],
                help="Choose multiple dietary restrictions if needed"
            )

        with st.expander("Meal Type", expanded=True):
            meal_type = st.selectbox(
                'Select meal type',
                ['Any', 'Breakfast', 'Lunch', 'Dinner', 'Dessert'],
                help="Choose the type of meal"
            )

        with st.expander("Additional Filters", expanded=True):
            rating_range = st.slider(
                'Rating Range',
                0.0, 5.0, (3.0, 5.0),
                step=0.5,
                help="Filter recipes by rating"
            )

            calories_range = st.slider(
                'Calories Range',
                0, 1000, (0, 1000),
                step=50,
                help="Filter recipes by calories"
            )

        

        submit_button = st.button('Find Recipes 🔍')

    # Main content
    if submit_button:
        with st.spinner('Finding your perfect recipes...'):
            filtered_df = filter_recipes(
                df, 
                dietary_restrictions, 
                meal_type,
                rating_range,
                calories_range
            )

        if not filtered_df.empty:
            st.success(f"Found {len(filtered_df)} matching recipes!")

            # Recipe results and statistics
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("### 📋 Recipe Results")
                recipe_df = filtered_df[['title', 'rating', 'meal_type', 'calories']].copy()
                recipe_df['rating'] = recipe_df['rating'].round(2)
                
                # Enhanced dataframe display
                st.dataframe(
                    recipe_df,
                    column_config={
                        "title": st.column_config.TextColumn("Recipe Name", width="large"),
                        "rating": st.column_config.NumberColumn("Rating", format="%.2f ⭐"),
                        "meal_type": "Meal Type",
                        "calories": st.column_config.NumberColumn("Calories", format="%d kcal")
                    },
                    hide_index=True,
                    height=400
                )

            with col2:
                st.markdown("### 📊 Recipe Statistics")
                
                # Metrics in cards
                with st.container():
                    st.metric(
                        "Average Rating",
                        f"{filtered_df['rating'].mean():.2f} ⭐",
                        delta=f"{filtered_df['rating'].mean() - df['rating'].mean():.2f} vs overall",
                        help="Average rating of filtered recipes"
                    )
                    st.metric(
                        "Average Calories",
                        f"{filtered_df['calories'].mean():.0f} kcal",
                        help="Average calories per serving"
                    )

            # Visualizations
            st.markdown("### 📈 Recipe Analytics")
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                st.plotly_chart(plot_meal_distribution(filtered_df), use_container_width=True)
            with viz_col2:
                st.plotly_chart(plot_rating_distribution(filtered_df), use_container_width=True)

            st.plotly_chart(plot_nutrition_comparison(filtered_df), use_container_width=True)

        else:
            st.error("No recipes found matching your criteria. Try adjusting your filters!")

if __name__ == '__main__':
    main()
