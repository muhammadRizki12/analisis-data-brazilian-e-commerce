import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime as dt
sns.set(style='dark')

# Import dataset
all_df = pd.read_csv("dashboard/all_data.csv")
 # change type str/obj -> datetime
datetime_columns = ["order_approved_at"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

def create_sum_order_items_df(df):
    sum_order_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_df = sum_order_df.rename(columns={"product_id": "count_x"})
    sum_order_df = sum_order_df.rename(columns={"product_category_name_english": "product_category"})
    sum_order_df = sum_order_df.sort_values(by="count_x", ascending=False)
    return sum_order_df

def create_review_score(df):
    review_scores = df["review_score"].value_counts().sort_values(ascending=False)
    df_cust = df['review_score']
    return review_scores, df_cust

def create_monthly_order(df):
    monthly_df = df.resample(rule='ME', on='order_approved_at').agg({
        "order_id": "nunique",
    })

    # mengubah format order_approved_at menjadi Tahun ke Bulan
    monthly_df.index = monthly_df.index.strftime('%B')
    monthly_df = monthly_df.reset_index()
    monthly_df.rename(columns={"order_id": "order_count", }, inplace=True)
    monthly_df = monthly_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')

    # monthly_df.sort_values(by='order_count')

    month_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    monthly_df["month_numeric"] = monthly_df["order_approved_at"].map(month_mapping)
    monthly_df = monthly_df.sort_values("month_numeric")
    monthly_df = monthly_df.drop("month_numeric", axis=1)
    return monthly_df

def create_rfm(df):
    now = dt.datetime(2018, 10, 20)

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    # Group by 'customer_id' and calculate Recency, Frequency, and Monetary
    recency = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_id'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    # Create a new DataFrame with the calculated metrics
    rfm = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })

    col_list = ['customer_id', 'Recency', 'Frequency', 'Monetary']
    rfm.columns = col_list
    return rfm

# Calling function
sum_order_df = create_sum_order_items_df(all_df)
review_scores_df, rating_service= create_review_score(all_df)
monthly_df = create_monthly_order(all_df)
rfm_df=create_rfm(all_df)

# SIDEBAR
with st.sidebar:
    st.markdown("## 📊 Dashboard E-commerce")
    st.markdown("---")

    st.markdown("#### 📝 Belajar Analisis Data dengan Python")
    st.markdown("**Nama:**  Muhammad Rizki")
    st.markdown("**Email:**  m.rizki.study@gmail.com")
    st.markdown("**ID Dicoding:**  muhammad_rizki23")

    st.markdown("---")

    st.markdown("### 📂 Dataset")
    st.link_button("🔗 Kaggle Dataset", "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")

    st.markdown("---")
    st.caption("© 2025 Muhammad Rizki")

st.header('Brazilian E-Commerce')

# Question 1
st.subheader("Best & Worst Performing Product")
col1, col2 = st.columns(2)
with col1:
    highest_product_sold=sum_order_df.max()[1]
    st.markdown(f"Higest Number : **{highest_product_sold}**")

with col2:
    lowest_product_sold=sum_order_df.min()[1]
    st.markdown(f"Lowest Number : **{lowest_product_sold}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="count_x", y="product_category", data=sum_order_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="count_x", y="product_category",
            data=sum_order_df.sort_values(by="count_x", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

# Question 2
st.subheader("Rating by customers for service")
st.markdown(f"Rating Average  : **{rating_service.mean():.2f}**")
most_common_score = review_scores_df.idxmax()

fig, ax = plt.subplots(figsize=(20, 10))
# Buat barplot tanpa warna custom dulu
barplot = sns.barplot(
    x=review_scores_df.index,
    y=review_scores_df.values,
    order=review_scores_df.index,
    color="#D3D3D3",  # default gray
)

# Warnai bar yang paling sering
for i, patch in enumerate(barplot.patches):
    score = review_scores_df.index[i]
    if score == most_common_score:
        patch.set_facecolor("#068DA9")  # warna biru

ax.set_title("Rating by customers for service", fontsize=30)
ax.set_xlabel("Rating")
ax.set_ylabel("Count")
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

# Question 3
st.subheader("Number of orders per month")
col1, col2 = st.columns(2)
with col1:
    high_order_num = monthly_df['order_count'].max()
    high_order_month = monthly_df[monthly_df['order_count'] == monthly_df['order_count'].max()]['order_approved_at'].values[0]
    st.markdown(f"Highest orders in {high_order_month} : **{high_order_num}**")
with col2:
    low_order_num = monthly_df['order_count'].min()
    low_order_month = monthly_df[monthly_df['order_count'] == monthly_df['order_count'].min()]['order_approved_at'].values[0]
    st.markdown(f"Lowest orders in {low_order_month} : **{low_order_num}**")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    monthly_df["order_approved_at"],
    monthly_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9",
)
plt.title("Number of Orders per Month", loc="center", fontsize=20)
plt.xticks(fontsize=10, rotation=25)
plt.yticks(fontsize=10)
st.pyplot(fig)

st.subheader("RFM Best Value")
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# beri comentar pada ax[index].set_xticks([]) bila ingin melihat customer nya by id

######################################3
tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

with tab1:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Recency",
        x="customer_id",
        data=rfm_df.sort_values(by="Recency", ascending=True).head(5),
        palette=colors,

    )
    plt.title("By Recency (Day)", loc="center", fontsize=18)
    plt.ylabel('')
    plt.xlabel("customer")
    plt.tick_params(axis='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with tab2:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Frequency",
        x="customer_id",
        data=rfm_df.sort_values(by="Frequency", ascending=False).head(5),
        palette=colors,

    )
    plt.ylabel('')
    plt.xlabel("customer")
    plt.title("By Frequency", loc="center", fontsize=18)
    plt.tick_params(axis='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with tab3:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Monetary",
        x="customer_id",
        data=rfm_df.sort_values(by="Monetary", ascending=False).head(5),
        palette=colors,
    )
    plt.ylabel('')
    plt.xlabel("customer")
    plt.title("By Monetary", loc="center", fontsize=18)
    plt.tick_params(axis='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)
