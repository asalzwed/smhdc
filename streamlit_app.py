import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df0 = pd.read_csv("data/smartpak_products.csv")
    df0["price"] = pd.to_numeric(df0["price"], errors="coerce")

    df1 = pd.read_csv("data/smartpak_ingredient_lookup.csv")
    return df0, df1

df, ingredients = load_data()

st.title("🧴 Supplement My Horse Dot Com")

# Sidebar filters
st.sidebar.header("Filter Products")

all_brands = sorted(df['brand'].dropna().unique())
brand_filter_mode = st.sidebar.selectbox("Filter by Brand", ["All", "Custom Selection"])
if brand_filter_mode == "Custom Selection":
    selected_brands = st.sidebar.multiselect("Select Brands", options=all_brands,default=['SmartPak Equine'])
else:
    selected_brands = all_brands  # Treat as 'All Selected'

# Category Child filter
all_children = df["category_child"].dropna().unique()
category_filter_mode = st.sidebar.selectbox("Filter by Category", ["All", "Custom Selection"])
if category_filter_mode == "Custom Selection":
    selected_categories = st.sidebar.multiselect("Select Categories", options=all_children,default=['Digestion'])
else:
    selected_categories = all_children  # Treat as 'All Selected'

# Price filter
min_price, max_price = float(df["price"].min()), float(df["price"].max())
price_range = st.sidebar.slider("Price Range ($):", min_value=min_price, max_value=max_price, value=(min_price, max_price))

# Product name search
search = st.sidebar.text_input("Search Product Name:")

# Display data
all_ingredient = ingredients["ingredient"].dropna().unique()
selected_ingredient = st.multiselect("Select Ingredient", options=all_ingredient, max_selections=1, default=['Chondroitin Sulfate (Bovine)'])
id_ing = ingredients[ingredients['ingredient'].isin(selected_ingredient)].drop_duplicates()

# Apply filters
filtered_df = df[
    df["brand"].isin(selected_brands) &
    df["category_child"].isin(selected_categories) &
    df["price"].between(price_range[0], price_range[1])

]

filtered_df = filtered_df.merge(id_ing[['product_id','ingredient', 'amount', 'unit']],left_on='id',right_on='product_id')

if search:
    filtered_df = filtered_df[filtered_df["name"].str.contains(search, case=False, na=False)]

st.markdown(f"### Showing {len(filtered_df)} product(s)")
st.dataframe(filtered_df.drop(columns=['id','product_id','category_parent']).reset_index(drop=True).rename(columns={'brand':'Brand',
'category_child':'Category',
'price':'Price ($)',
'name':'Product Name'}),
hide_index=True,
column_config={
    "url": st.column_config.LinkColumn("Link",display_text="🔗",width="small")})


# Option to download filtered data
st.download_button("📥 Download Filtered CSV", filtered_df.to_csv(index=False), file_name="filtered_smartpak_products.csv")

