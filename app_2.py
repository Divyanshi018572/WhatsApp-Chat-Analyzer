import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

import preprocess
import connector

# ----------------- Main Page / Welcome -----------------
st.title("📊 WhatsApp Chat Analyzer")

st.markdown("""
Welcome to the *WhatsApp Chat Analyzer*!  
Upload your WhatsApp chat export file to uncover insightful stats, timelines, word clouds, emoji usage, and more.

---
### 👇 How to Use:
1. Upload your exported WhatsApp chat `.txt` file using the sidebar  
2. Select a user or choose **Overall**  
3. Click **Show Analysis** to view full statistics  

> Fun Fact: Why don't scientists trust atoms?  
> Because they *make up everything!* ⚛😄
""")

# ----------------- Sidebar -----------------
st.sidebar.title("Upload File")
uploaded_file = st.sidebar.file_uploader("Choose WhatsApp chat file (.txt)", type=["txt"])

if uploaded_file is not None:
    data = uploaded_file.getvalue().decode("utf-8")
    df = preprocess.preprocessor(data)

    # Unique users
    user_list = df["user"].unique().tolist()
    if "notification" in user_list:
        user_list.remove("notification")

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    # ----------------- Analysis Button -----------------
    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = connector.fetch_stats(selected_user, df)

        # TOP STATS
        st.title("📌 Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Messages")
            st.title(num_messages)
        with col2:
            st.header("Words")
            st.title(words)
        with col3:
            st.header("Media")
            st.title(num_media_messages)
        with col4:
            st.header("Links")
            st.title(num_links)

        # ----------------- Monthly Timeline -----------------
        st.subheader("📆 Monthly Timeline")
        timeline = connector.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["message"])
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # ----------------- Daily Timeline -----------------
        st.subheader("📅 Daily Timeline")
        daily_timeline = connector.daily_time(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline["only_date"], daily_timeline["message"], color="black")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # ----------------- Busy Users -----------------
        if selected_user == "Overall":
            st.subheader("👥 Most Busy Users")
            x, new_df = connector.most_busy_user(df)

            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # ----------------- Most Common Words -----------------
        st.subheader("📝 Most Common Words")
        most_common_df = connector.most_common_words(selected_user, df)
        st.dataframe(most_common_df)

        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # ----------------- Wordcloud -----------------
        st.subheader("☁ Wordcloud")
        df_wc = connector.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # ----------------- Emoji Analysis -----------------
        st.subheader("😀 Emoji Analysis")
        emoji_df = connector.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

        # ----------------- Activity Maps -----------------
        st.subheader("📊 Activity Map")

        col1, col2 = st.columns(2)
        with col1:
            st.write("Most Busy Day")
            busy_day = connector.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)

        with col2:
            st.write("Most Busy Month")
            busy_month = connector.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="orange")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # ----------------- Heatmap -----------------
        st.subheader("🔥 Weekly Activity Heatmap")
        user_heatmap = connector.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)
