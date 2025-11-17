import streamlit as st
import preprocess, connector
import matplotlib.pyplot as plt
import seaborn as sns

# ----------------- Main Page / Welcome -----------------
st.title("📊 WhatsApp Chat Analyzer")
st.markdown("""
Welcome to the *WhatsApp Chat Analyzer*!  
Upload your WhatsApp chat export file to uncover insightful stats, timelines, word clouds, emoji usage, and much more.

---
*How to Use:*  
1. Upload your exported WhatsApp chat text file using the sidebar.  
2. Select a user or choose "Overall" for group-wide analysis.  
3. Click *Show Analysis* and explore your chat data!

> Why don’t scientists trust atoms?  
> Because they make up everything! ⚛😄
""")

# Sidebar title
st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocess.preprocessor(data)

    # fetch unique users
    user_list = df["user"].unique().tolist()
    user_list.remove("notification")
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = connector.fetch_stats(selected_user, df)
        st.title("TOP STATISTICS")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        timeline = connector.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["message"])
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # daily timeline
        daily_timeline = connector.daily_time(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline["only_date"], daily_timeline["message"], color="black")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

        # finding the busiest users in the group
        if selected_user == "Overall":
            st.title("Most busy users")
            x, new_df = connector.most_busy_user(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values)
                plt.xticks(rotation="vertical")
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # most common words
        most_common_df = connector.most_common_words(selected_user, df)
        st.dataframe(most_common_df)

        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation="vertical")

        st.title("Most Common Words")
        st.pyplot(fig)

        # wordcloud
        st.title("Wordcloud")
        df_wc = connector.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # emoji analysis
        emoji_df = connector.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most busy Day")
            busy_day = connector.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)
        with col2:
            st.header("Most busy Month")
            busy_month = connector.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = connector.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)



