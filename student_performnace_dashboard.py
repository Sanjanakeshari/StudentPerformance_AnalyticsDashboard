# =========================
# STUDENT PERFORMANCE ANALYTICS DASHBOARD
# =========================

# Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Display settings
pd.set_option('display.max_columns', None)
sns.set(style="whitegrid")

print("Libraries imported successfully!\n")

# =========================
# STEP 1: LOAD DATASET
# =========================
df = pd.read_csv("student_performance_data.csv")

print("Original Dataset Loaded Successfully!")
print("First 5 Rows:\n")
print(df.head())

# =========================
# STEP 2: BASIC INFO
# =========================
print("\n=========================")
print("DATASET INFORMATION")
print("=========================")
print("Dataset Shape:", df.shape)
print("\nColumn Names:")
print(df.columns)
print("\nData Types:")
print(df.dtypes)
print("\nMissing Values:")
print(df.isnull().sum())

# =========================
# STEP 3: RENAME COLUMNS
# =========================
df.rename(columns={"Attendance(%)": "Attendance"}, inplace=True)

# =========================
# STEP 4: REMOVE EMPTY ROWS
# =========================
df.dropna(how='all', inplace=True)

# =========================
# STEP 5: DATA CLEANING
# =========================
df.columns = df.columns.str.strip()

df["Marks"] = pd.to_numeric(df["Marks"], errors='coerce')
df["Attendance"] = pd.to_numeric(df["Attendance"], errors='coerce')
df["Logins"] = pd.to_numeric(df["Logins"], errors='coerce')

# Fill missing numeric values with median
df["Marks"] = df["Marks"].fillna(df["Marks"].median())
df["Attendance"] = df["Attendance"].fillna(df["Attendance"].median())
df["Logins"] = df["Logins"].fillna(df["Logins"].median())

# Fill missing text values
df["Status"] = df["Status"].fillna("Unknown")
df["Name"] = df["Name"].fillna("Unknown")

print("\nData cleaned successfully!")
print("\nCleaned Data Info:")
print(df.info())

# =========================
# STEP 6: FEATURE ENGINEERING
# =========================
def performance_category(marks):
    if marks >= 85:
        return "Excellent"
    elif marks >= 70:
        return "Good"
    elif marks >= 50:
        return "Average"
    else:
        return "Poor"

def attendance_category(att):
    if att >= 85:
        return "High Attendance"
    elif att >= 70:
        return "Moderate Attendance"
    else:
        return "Low Attendance"

df["Performance_Category"] = df["Marks"].apply(performance_category)
df["Attendance_Category"] = df["Attendance"].apply(attendance_category)
df["Engagement_Score"] = (df["Attendance"] * 0.4) + (df["Logins"] * 1.5) + (df["Marks"] * 0.6)

print("\nFeature Engineering Completed!")
print(df.head())

# =========================
# STEP 7: SUMMARY STATISTICS
# =========================
print("\n=========================")
print("SUMMARY STATISTICS")
print("=========================")
print(df.describe())

# =========================
# STEP 8: KPI METRICS
# =========================
total_students = df["StudentID"].nunique()
avg_marks = round(df["Marks"].mean(), 2)
avg_attendance = round(df["Attendance"].mean(), 2)
avg_logins = round(df["Logins"].mean(), 2)
at_risk_students = df[df["Status"].isin(["At Risk", "Critical"])].shape[0]

print("\n=========================")
print("KPI SUMMARY")
print("=========================")
print(f"Total Students       : {total_students}")
print(f"Average Marks        : {avg_marks}")
print(f"Average Attendance   : {avg_attendance}%")
print(f"Average Logins       : {avg_logins}")
print(f"At Risk/Critical     : {at_risk_students}")

# =========================
# STEP 9: STATUS COUNTS
# =========================
print("\n=========================")
print("STUDENT STATUS DISTRIBUTION")
print("=========================")
print(df["Status"].value_counts())

# =========================
# STEP 10: SAVE CLEANED DATA
# =========================
df.to_csv("cleaned_student_performance_data.csv", index=False)
print("\nCleaned dataset saved as 'cleaned_student_performance_data.csv'")

# =========================
# STEP 11: VISUALIZATIONS
# =========================

# 1. Status Distribution
plt.figure(figsize=(8,5))
sns.countplot(data=df, x="Status", order=df["Status"].value_counts().index)
plt.title("Student Status Distribution")
plt.xlabel("Status")
plt.ylabel("Count")
plt.show()

# 2. Marks Distribution
plt.figure(figsize=(8,5))
sns.histplot(df["Marks"], bins=10, kde=True)
plt.title("Distribution of Student Marks")
plt.xlabel("Marks")
plt.ylabel("Frequency")
plt.show()

# 3. Attendance vs Marks
plt.figure(figsize=(8,5))
sns.scatterplot(data=df, x="Attendance", y="Marks", hue="Status")
plt.title("Attendance vs Marks")
plt.xlabel("Attendance (%)")
plt.ylabel("Marks")
plt.show()

# 4. Performance Category Distribution
plt.figure(figsize=(8,5))
sns.countplot(data=df, x="Performance_Category", order=df["Performance_Category"].value_counts().index)
plt.title("Performance Category Distribution")
plt.xlabel("Performance Category")
plt.ylabel("Count")
plt.show()

# 5. Top 10 Students by Marks
top_students = df.sort_values(by="Marks", ascending=False).head(10)

plt.figure(figsize=(10,6))
sns.barplot(data=top_students, x="Marks", y="Name")
plt.title("Top 10 Students by Marks")
plt.xlabel("Marks")
plt.ylabel("Student Name")
plt.show()

# 6. Correlation Heatmap
plt.figure(figsize=(8,5))
corr = df[["Marks", "Attendance", "Logins", "Engagement_Score"]].corr()
sns.heatmap(corr, annot=True, cmap="Blues")
plt.title("Correlation Heatmap")
plt.show()

# =========================
# STEP 12: STUDENT RECOMMENDATIONS
# =========================
recommendation_df = df[
    (df["Marks"] < 50) | 
    (df["Attendance"] < 60) | 
    (df["Status"].isin(["At Risk", "Critical"]))
].copy()

recommendation_df["Recommendation"] = np.where(
    recommendation_df["Marks"] < 50,
    "Needs academic improvement",
    "Monitor attendance and engagement"
)

print("\n=========================")
print("RECOMMENDATION DATA")
print("=========================")
print(recommendation_df.head())

recommendation_df.to_excel("student_recommendation.xlsx", index=False)
print("\nRecommendation file saved as 'student_recommendation.xlsx'")

# =========================
# STEP 13: MYSQL INTEGRATION
# =========================
# Replace these with your actual MySQL details
username = "root"
password = "your_password"
host = "localhost"
database_name = "student_dashboard"

try:
    engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}/{database_name}")
    print("\nMySQL connection created successfully!")

    # Save data to MySQL
    df.to_sql("student_performance", con=engine, if_exists="replace", index=False)
    print("Data uploaded to MySQL successfully!")

    # SQL Query 1: Top Performers
    query1 = """
    SELECT StudentID, Name, Marks, Attendance, Status
    FROM student_performance
    ORDER BY Marks DESC
    LIMIT 10;
    """
    top_performers = pd.read_sql(query1, con=engine)
    print("\nTop Performers:")
    print(top_performers)

    # SQL Query 2: At Risk Students
    query2 = """
    SELECT StudentID, Name, Marks, Attendance, Logins, Status
    FROM student_performance
    WHERE Status IN ('At Risk', 'Critical');
    """
    at_risk_df = pd.read_sql(query2, con=engine)
    print("\nAt Risk Students:")
    print(at_risk_df)

    # SQL Query 3: Average Metrics
    query3 = """
    SELECT 
        ROUND(AVG(Marks), 2) AS Avg_Marks,
        ROUND(AVG(Attendance), 2) AS Avg_Attendance,
        ROUND(AVG(Logins), 2) AS Avg_Logins
    FROM student_performance;
    """
    avg_metrics = pd.read_sql(query3, con=engine)
    print("\nAverage Metrics:")
    print(avg_metrics)

    # SQL Query 4: Status-wise Student Count
    query4 = """
    SELECT Status, COUNT(*) AS Student_Count
    FROM student_performance
    GROUP BY Status;
    """
    status_summary = pd.read_sql(query4, con=engine)
    print("\nStatus Summary:")
    print(status_summary)

except Exception as e:
    print("\nMySQL part skipped because of connection issue:")
    print(e)

# =========================
# STEP 14: FINAL CONCLUSION
# =========================
print("\n=========================")
print("PROJECT COMPLETED SUCCESSFULLY ✅")
print("=========================")
print("""
This dashboard project helps in:
1. Tracking student academic performance
2. Identifying at-risk students
3. Measuring attendance and engagement
4. Supporting data-driven academic decisions
5. Exporting recommendations for intervention
""")
