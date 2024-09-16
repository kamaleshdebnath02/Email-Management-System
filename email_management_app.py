
import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu

# Set page configuration
st.set_page_config(page_title="Email Management System", layout="wide")

# Custom CSS styles using Streamlit's built-in features
def apply_styles():
    st.markdown("""
        <style>
        /* Import a professional font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Roboto', sans-serif;
            background-color: #f5f5f5;
            color: #333333;
        }

        /* Center the headers */
        h1, h2, h3, h4, h5, h6 {
            text-align: center;
            color: #6439FF;
        }

        /* Style buttons */
        .stButton > button {
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5em 1em;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #1a252f;
        }

        /* Style selectbox */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
        }
        div[data-baseweb="select"] * {
            color: #333333 !important;
        }

        /* Style file uploader */
        .stFileUploader label {
            color: #333333;
        }

        /* Style dataframes */
        .stDataFrame {
            background-color: #ffffff;
            color: #333333;
        }

        /* Style tabs */
        div[role="tablist"] > div {
            background: transparent;
        }
        div[role="tab"] {
            color: #2c3e50;
            font-weight: bold;
        }
        div[role="tab"][aria-selected="true"] {
            border-bottom: 2px solid #2c3e50;
        }

        /* Style option menu */
        ul[data-testid="stHorizontalBlock"] {
            background-color: transparent;
            padding: 0;
            margin: 0;
        }
        ul[data-testid="stHorizontalBlock"] > li {
            display: inline-block;
            margin-right: 1em;
        }
        ul[data-testid="stHorizontalBlock"] > li > a {
            color: #2c3e50;
            text-decoration: none;
            font-size: 18px;
            padding: 0.5em 1em;
            border-radius: 4px;
            transition: background-color 0.3s, color 0.3s;
        }
        ul[data-testid="stHorizontalBlock"] > li > a:hover {
            background-color: #e1e1e1;
            color: #2c3e50;
        }
        ul[data-testid="stHorizontalBlock"] > li > a.active {
            background-color: #2c3e50;
            color: #ffffff;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #e1e1e1;
        }
        ::-webkit-scrollbar-thumb {
            background: #888888;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555555;
        }

        /* Style data editor (if used) */
        [data-testid="stDataFrame"] {
            background-color: #ffffff;
            color: #333333;
        }

        /* Style success messages */
        .stSuccess {
            background-color: #dff0d8;
            color: #fffff;
        }

        /* Style warning messages */
        .stWarning {
            background-color: #fcf8e3;
            color: #8a6d3b;
        }

        /* Style error messages */
        .stError {
            background-color: #f2dede;
            color: #a94442;
        }

        
        
        </style>
        """, unsafe_allow_html=True)



# Apply custom styles
apply_styles()

def clean_email_data(df, email_column='email'):
    # Convert to string type to handle non-string entries
    df[email_column] = df[email_column].astype(str)
    
    # Convert to lowercase and strip whitespace
    df[email_column] = df[email_column].str.strip().str.lower()
    
    # Remove rows with missing or empty emails
    df = df[df[email_column].notnull()]
    df = df[df[email_column] != '']
    
    # Remove duplicates within the uploaded file
    df = df.drop_duplicates(subset=email_column)
    
    return df

def find_duplicates(uploaded_emails, database_emails):
    # Identify duplicates between uploaded_emails and database_emails
    duplicates = uploaded_emails[uploaded_emails.isin(database_emails)].reset_index(drop=True)
    unique_emails = uploaded_emails[~uploaded_emails.isin(database_emails)].reset_index(drop=True)
    return duplicates, unique_emails

def update_main_database(unique_emails_df, database_path):
    # Append unique emails to the main database
    if os.path.exists(database_path):
        df_database = pd.read_csv(database_path)
        df_database['email'] = df_database['email'].str.strip().str.lower()
        df_database.drop_duplicates(subset='email', inplace=True)
    else:
        df_database = pd.DataFrame(columns=['email'])
        
    updated_db = pd.concat([df_database, unique_emails_df]).drop_duplicates(subset='email').reset_index(drop=True)
    
    # Save the updated database
    updated_db.to_csv(database_path, index=False)
    return updated_db

def upload_csv_page(df_database, database_path):
    st.header("📤 Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            
            # Let the user select the email column
            email_column = st.selectbox("Select the email column", df_uploaded.columns.tolist())
            
            # Clean the uploaded data
            df_uploaded = clean_email_data(df_uploaded, email_column)
            
            if df_uploaded.empty:
                st.warning("No valid email addresses found in the uploaded file.")
                return
            
            st.subheader("Cleaned Uploaded Data")
            st.dataframe(df_uploaded.head(), height=200)
            
            # Find duplicates
            uploaded_emails = df_uploaded[email_column]
            database_emails = df_database['email']
            
            duplicates, unique_emails = find_duplicates(uploaded_emails, database_emails)
            
            # Display results using tabs
            tab1, tab2 = st.tabs(["🚫 Duplicates", "✅ Unique Emails"])
            
            with tab1:
                st.subheader("Duplicate Email IDs")
                if not duplicates.empty:
                    st.write(duplicates.to_frame(name='email'))
                    # Download duplicates
                    csv_duplicates = duplicates.to_frame(name='email').to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Duplicates as CSV",
                        data=csv_duplicates,
                        file_name='duplicate_emails.csv',
                        mime='text/csv',
                    )
                else:
                    st.write("No duplicates found.")
            
            with tab2:
                st.subheader("Unique Email IDs")
                if not unique_emails.empty:
                    st.write(unique_emails.to_frame(name='email'))
                    # Download unique emails
                    csv_unique = unique_emails.to_frame(name='email').to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Unique Emails as CSV",
                        data=csv_unique,
                        file_name='unique_emails.csv',
                        mime='text/csv',
                    )
                    
                    # Option to update the main database
                    if st.button("Update Main Database with Unique Emails"):
                        unique_emails_df = unique_emails.to_frame(name='email')
                        updated_db = update_main_database(unique_emails_df, database_path)
                        st.success("Main database has been updated.")
                else:
                    st.write("No unique emails to add to the database.")
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.error("Please ensure the uploaded file is a valid CSV and try again.")

def view_database_page(df_database, database_path):
    st.header("📂 Main Database")
    
    if not df_database.empty:
        st.subheader("Current Email Database")
        st.dataframe(df_database, height=400)
        # Download main database
        csv_database = df_database.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Main Database as CSV",
            data=csv_database,
            file_name='emails_db.csv',
            mime='text/csv',
        )
    else:
        st.write("The main database is currently empty.")

def main():
    apply_styles()
    # Main application
    st.title("✨ Email Management System")
    st.write("""
    Welcome to the Email Management System. This application allows you to:
    - Upload a CSV file containing email IDs.
    - Detect duplicates with the existing database.
    - Remove duplicate emails.
    - Download the processed files.
    - Update the main database with new unique email IDs.
    """)
    
    # Load the main database
    database_path = 'emails_db.csv'
    if os.path.exists(database_path):
        df_database = pd.read_csv(database_path)
        if 'email' not in df_database.columns:
            st.error("The 'email' column is not present in the main database.")
            return
        else:
            df_database['email'] = df_database['email'].str.strip().str.lower()
            df_database.drop_duplicates(subset='email', inplace=True)
    else:
        st.warning("Main database not found. A new one will be created upon updating.")
        df_database = pd.DataFrame(columns=['email'])
    
    # Streamlit option menu
    selected = option_menu(
    menu_title=None,
    options=["Upload CSV", "View Database"],
    icons=["cloud-upload", "database"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "nav-link": {
            "font-size": "18px",
            "font-weight": "bold",
            "text-decoration": "none",
        },
        "nav-link-selected": {
            "background-color": "#2c3e50",
            "color": "#ffffff",
        },
    }
)

    
    if selected == "Upload CSV":
        upload_csv_page(df_database, database_path)
    elif selected == "View Database":
        view_database_page(df_database, database_path)

if __name__ == "__main__":
    main()
