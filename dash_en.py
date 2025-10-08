import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pydeck as pdk
import matplotlib.pyplot as plt
# These libraries are for handling bidirectional text (e.g., Arabic) in charts
import arabic_reshaper
from bidi.algorithm import get_display

# Set Matplotlib to use a font that supports Arabic characters
# You might need to install an appropriate font on your system,
# e.g., 'Amiri', 'DejaVu Sans', or 'Arial' if you're on a common OS.
# For Streamlit Cloud, you need to ensure the font is available.
# A common choice is 'DejaVu Sans' which often has broad coverage.
# If Arabic characters don't display, this is the most likely culprit.
plt.rcParams['font.family'] = 'DejaVu Sans' # Safe default, but might not handle Arabic well

st.set_page_config(
    page_title="Unforgotten Trace",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Load Data
# -------------------------------
# NOTE: The commented-out code is better practice for a deployable app, 
# as it uses st.cache_data and a remote URL. 
# For this correction, I'll assume 'under_18_9.csv' is locally available.

# url = "https://raw.githubusercontent.com/Luay-alhammada/Unforgeten_trace/main/under_18_8.csv"

# @st.cache_data
# def load_data(url):
#     return pd.read_csv(url)

# df = load_data(url)

# --- CORRECTION: Assuming local file 'under_18_9.csv' is correct ---
# A better practice would be to use @st.cache_data
# @st.cache_data

url = "https://raw.githubusercontent.com/Luay-alhammada/Unforgeten_trace/refs/heads/main/under_18_9_en.csv"

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

df = load_data(url)


# Data Preprocessing
df['date_in'] = pd.to_datetime(df['date_in'], errors='coerce')

# Ensure lat/lon are numeric
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

# -------------------------------
# Page Title
# -------------------------------
st.markdown("<h4 style='text-align: center;'>Children in the Records of the Air Force Intelligence Investigation Branch</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: left;'>
<h4>• <b>Topic:</b> Violations against children (under the age of 18)</h4>
<h4>• <b>Time Period:</b> 2011 to 2016</h4>
<h4>• <b>Total Records:</b> 1600 entries</h4>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# Layout: Left (Filters), Middle (Map), Right (Text)
# -------------------------------
# CORRECTION: Removed 'col4' which was declared but never used,
# and re-ordered the columns for a clear Left (col1), Middle (col2), Right (col3) flow.
col1, col2, col3, col4 = st.columns([1, 4,1, 4]) 

# -------------------------------
# Left Column: Filters
# -------------------------------
with col1:
    st.header("Filters")
    # Ensure there are valid years before proceeding
    valid_years = df['date_in'].dt.year.dropna().unique().astype(int)
    if valid_years.size > 0:
        years = sorted(valid_years, reverse=True)
        years_with_all = ['All Years'] + [str(y) for y in years] # Convert years to strings for consistent selectbox options
        selected_year_str = st.selectbox("Select Year", years_with_all)
        
        # Filter the DataFrame based on the selection
        if selected_year_str == "All Years":
            df_filtered = df.copy()
        else:
            selected_year = int(selected_year_str)
            df_filtered = df[df['date_in'].dt.year == selected_year]
    else:
        st.warning("No valid 'date_in' values found for year filtering.")
        df_filtered = df.copy() # Use full data if no valid dates

# -------------------------------
# Middle Column: PyDeck Map
# -------------------------------
with col2:
    st.markdown("<h4>1 - Birthplaces of the Detainees</h4>", unsafe_allow_html=True)
    st.markdown("""
<div style='font-size: 16px;'>
About 40% of the names include information about their birthplace.
</div><br>
""", unsafe_allow_html=True)

    # Aggregate counts per birthplace for the filtered data
    df_counts = df_filtered.groupby("birthplace").size().reset_index(name="count")
    # Use first non-null lat/lon for each birthplace. This assumes 'birthplace' has lat/lon data.
    # We must ensure to drop any NaN values after the merge/groupby
    df_coords = df_filtered.groupby("birthplace")[["lat", "lon"]].first().reset_index()
    df_map = df_counts.merge(df_coords, on="birthplace", how="left")
    df_map = df_map.dropna(subset=["lat", "lon"])

    # Scale radius
    if not df_map.empty and df_map["count"].nunique() > 1:
        scaler = MinMaxScaler((5, 20))
        df_map["radius"] = scaler.fit_transform(df_map[["count"]])
    elif not df_map.empty:
        # Handle case where all counts are the same (e.g., only one point or one count value)
        df_map["radius"] = 15 # A default size
    else:
        st.info("No data points with valid coordinates for this year selection.")
        # Create an empty PyDeck map to avoid errors
        r = pdk.Deck(layers=[], initial_view_state=pdk.ViewState(latitude=34.8, longitude=38, zoom=6), map_style="light")
        st.pydeck_chart(r)
        
    if not df_map.empty:
        # PyDeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position=["lon", "lat"],
            get_radius="radius",
            get_fill_color=[200, 30, 0, 160],
            pickable=True,
            radius_units="pixels",
        )

        view_state = pdk.ViewState(latitude=34.8, longitude=38, zoom=6)

        tooltip = {
            "html": "<b>Birthplace:</b> {birthplace}<br/><b>Cases:</b> {count}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }

        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="light"
        )

        st.pydeck_chart(r)


# -------------------------------
# Right Column: Text / Introduction
# -------------------------------
with col4:
    st.markdown("<h3>Introduction</h3>", unsafe_allow_html=True)
    st.markdown("""
<div>
After the collapse of the Syrian regime on December 8, 2024, a large collection of sensitive intelligence documents was leaked, including records from the Investigation Branch of the Air Force Intelligence Directorate. These materials came in the form of documents, spreadsheets (Excel), text files (Word), images, and PDFs. The information was extracted from scanned documents and merged into an integrated database.

The data underwent careful cleaning and classification, with continuous verification to ensure accuracy and reliability. This report presents a focused analysis on cases of children under 18 years old, as part of a series of analytical studies that will be published later, addressing different themes from these records.

The total size of the constructed database is about 100,000 rows, each representing an independent data point. Various techniques were applied to filter and extract records relevant to minors. Initial findings indicate that at least 1,600 children were mentioned in these records. This number does not represent the total count but only what was identified in documents covering the period from 2011 to 2016.

The leaked records contained detailed classifications from the source, including: arrest date, file transfer date, file return date, release date, birth date, death date, offense, branch chief’s recommendation, and the general’s decision.

In this report, the analysis begins with detainees’ birthplaces, followed by the patrols responsible for the arrests and the intelligence branches to which detainees were transferred. It also examines the types of investigators, departments, and committees involved. The report further discusses the nature of the charges brought against detainees and the final outcomes of their cases. It concludes with a visual chart showing the temporal distribution of detainee numbers during those years, along with selected excerpts from the records.
</div>
""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# New Row: Patrols and Investigators

# CORRECTION: Re-indexed column variables (col5, col6, col7, col8)
# to match the desired [1, 4, 1, 4] layout more clearly. 
# col5 is unused (spacer), col6 is Chart 3, col7 is unused (spacer), col8 is Chart 2.
# Renamed for clarity: col_left_spacer, col_chart_3, col_right_spacer, col_chart_2
col_left_spacer, col_chart_3, col_right_spacer, col_chart_2 = st.columns([1, 4, 1, 4])

with col_chart_2:
    st.markdown("<h4>2 - Names of the Patrols That Carried Out the Arrests</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div>
      An analysis of the leaked documents revealed around 50 different entities belonging to several security and military agencies that were responsible for arresting and transferring detainees to the Investigation Branch of the Air Force Intelligence Directorate. The chart shows the top ten patrols that were the most active.
    </div>
    """, unsafe_allow_html=True)
    
    if 'arresting_patrol' in df_filtered.columns:
        # Get the top 11 categories and their counts
        pie_counts = df_filtered['arresting_patrol'].value_counts().head(11)

        # Exclude the 'no_value' category
        pie_counts = pie_counts[pie_counts.index != 'no_value']

        if not pie_counts.empty:
            # Prepare legend labels
            legend_labels = [
                get_display(arabic_reshaper.reshape(f"{cat}"))
                for cat in pie_counts.index
            ]

            # Function: show only counts
            def autopct_counts(pct, all_vals):
                absolute = int(round(pct/100.*sum(all_vals)))
                return str(absolute)

            # Create the pie chart figure and axis
            fig, ax = plt.subplots(figsize=(3, 3))

            ax.pie(
                pie_counts.values,
                labels=None,  # No labels on the slices themselves
                autopct=lambda pct: autopct_counts(pct, pie_counts.values),  # Show only counts
                startangle=90,
                textprops={'fontsize':6}
            )
            # Add a legend outside the chart
            ax.legend(
                legend_labels,
                loc="center left",
                bbox_to_anchor=(1.1, 0.5),  # Adjust to fit
                fontsize=5,
                frameon=False
            )

            # Ensure the pie is a circle
            ax.axis('equal')

            # Display the chart in Streamlit
            # CORRECTION: Removed plt.tight_layout() here as it often conflicts with Bidi/Arabic and external legends
            st.pyplot(fig)
        else:
            st.info("No 'arresting_patrol' data for the selected year.")
    else:
        st.warning("Column 'arresting_patrol' not found in the data.")


with col_chart_3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-bottom: 5px;'>3 - Investigators and Departments Inside the Branch</h4>", unsafe_allow_html=True)
    st.markdown("""
<div>
    <p>Within the branch, the data shows two categories of investigators:</p>
    <ul style='margin-top: 5px;'>
        <li>
            <strong>First category:</strong>
            Includes investigators whose names were not mentioned but instead were referred to by codes (e.g., Th4, Z10, L2). It is likely that this was done to maintain their anonymity, especially given their role in extracting confessions through torture methods.
        </li>
        <li>
            <strong>Second category:</strong>
            Includes investigators whose first or full names were mentioned. In some cases, the records referred to the department or committee responsible for the interrogation instead of a specific investigator's name.<br>
            From my experience at the Mezzeh Branch, interrogation procedures began with beating and torture in the branch yard to extract confessions. After the confession, I was transferred to another room where a different investigator sat behind his desk and played the role of the “polite interrogator.”
        </li>
    </ul>
    <br>
    <p><strong>Military ranks involved in the interrogations:</strong></p>
    <ul style='margin-top: 5px;'>
        <li>Major, Captain, Lieutenant, First Lieutenant, Warrant Officer, Brigadier General, Colonel.</li>
    </ul>
    <br>
    <p><strong>Departments and committees mentioned in the records:</strong></p>
    <ul style='margin-top: 5px;'>
        <li>
            <p>Department of Organizations and Extremist Currents - Department of Criminal and Economic Investigations - Department of Security and Counter-Terrorism Investigations - Department of Disciplinary and Conduct Investigations.</p>
        </li>
        <li>
            <p>First Committee - Second Committee - First + Second Committee - Field Committee - Committee for Interrogation of Hostile Individuals.</p><br><br>
        </li>
    </ul>
</div>
""", unsafe_allow_html=True)


# New Row: Charges and Places of Detention

# CORRECTION: Re-indexed column variables (col9, col10, col11, col12)
# Renamed for clarity: col_left_spacer2, col_chart_5, col_right_spacer2, col_text_4
col_left_spacer2, col_chart_5, col_right_spacer2, col_text_4 = st.columns([1, 4, 1, 4])

with col_chart_5:
    st.markdown("<h5 style='text-align: left;'>5 - Places of Detention in Air Force Intelligence</h5>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: left; font-size: 18px; line-height: 1.8;'>
        Regarding the detention locations, the data revealed about forty different places of arrest or detention.
        The chart above shows the top 15 locations mentioned, such as <b>New Mezzeh</b> and <b>Old Mezzeh</b>.
        This is the specific location where I was personally detained.
        <br>
        The dataset also includes scattered details such as numbers or officer names that require further research 
        to verify whether they represent actual locations or were mistakenly included.
        </div><br>
        """,
        unsafe_allow_html=True
    )
    
    if 'Place of Arrest' in df_filtered.columns:
        # Count values from the filtered DataFrame
        # IMPORTANT: Use ascending=True so the largest bar appears at the top of the chart.
        bar_counts = df_filtered['Place of Arrest'].value_counts().head(15).sort_values(ascending=True)

        if not bar_counts.empty:
            # Prepare labels for the y-axis (now that the chart is horizontal)
            labels = [
                get_display(arabic_reshaper.reshape(f"{cat}"))
                for cat in bar_counts.index
            ]

            # Create the horizontal bar chart
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # CHANGE 1: Use barh for horizontal bars
            bars = ax.barh(labels, bar_counts.values)

            # CHANGE 2: Adjust label placement for horizontal bars
            for bar in bars:
                width = bar.get_width() # For barh, width is the bar length (the count)
                label_x_pos = width + 7 # Position text slightly past the end of the bar
                ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                        va='center', ha='left', fontsize=16) # ha='left' anchors the text after the bar

            # CHANGE 3: Update tick configuration (Y-axis labels are fine, X-axis ticks are removed)
            ax.tick_params(axis='y', labelsize=18)
            ax.set_xlabel('')    # Remove X-axis label
            ax.set_xticks([])    # Remove X-axis tick marks
            # Original rotation is removed because X-axis is now removed

            # Remove spines for a cleaner look (including the bottom one now that there are no x-ticks)
            ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)

            # CHANGE 4: Add vertical gridlines (axis='x')
            plt.grid(axis='x', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)

            # Removed plt.tight_layout() as per previous discussion for Arabic label display.
            st.pyplot(fig)
        else:
             st.info("No 'Place of Arrest' data for the selected year.")
    else:
        st.warning("Column 'Place of Arrest' not found in the data.")

with col_text_4:
    st.markdown("<h4 style='text-align: left;'>4 - The Charges</h4>", unsafe_allow_html=True)

    st.markdown("""
<div style='text-align: left; font-size: 16px;'>
The charges were arranged from the most frequent to the least frequent, based on the data provided. 
These charges apply to both children and adults who were detained together:

1. <b>Participation in demonstrations and riots:</b> Includes participating in demonstrations, riots, vandalism, incitement to protest, resisting patrols, chanting anti-state slogans, and throwing stones at security forces. Some cases involved holding offensive signs, flags, or writing slogans on walls.
2. <b>Membership in armed terrorist groups:</b> Includes joining various armed groups, participating in terrorist operations against the army and security, setting up roadblocks, and possessing weapons.
3. <b>Collaboration with militants:</b> Includes providing material and logistical support, transporting weapons and ammunition, offering shelter, and sharing information.
4. <b>Incitement:</b> Includes inciting protests, sectarian incitement, and encouraging soldiers to defect.
5. <b>Suspicious security status:</b> Includes monitoring checkpoints and government facilities, possessing offensive media on phones, or not obeying patrol orders.
6. <b>Communication with terrorists:</b> Includes contacting individuals known to belong to terrorist groups and exchanging information with them.
7. <b>Miscellaneous:</b> Includes theft, forgery, impersonation of security personnel, vandalism of public property, and attempting illegal departure from the country.
</div>
""", unsafe_allow_html=True)
    

# New Row: Referrals and Outcomes

# CORRECTION: Re-indexed column variables (col14, col15, col16, col17)
# Renamed for clarity: col_left_spacer3, col_text_7, col_right_spacer3, col_chart_6
col_left_spacer3, col_text_7, col_right_spacer3, col_chart_6 = st.columns([1, 4, 1, 4])

with col_text_7:
    st.markdown("<h4 style='text-align: left;'>7 - Referral Pathways</h4>", unsafe_allow_html=True)
    st.markdown("""
<div style='text-align: left;'>
The data shows that children were referred to several different entities. The largest proportion of referrals were to release orders, 
followed by referrals to the Public Prosecution, Military Court, and the Counter-Terrorism Court. Around 100 cases had no referral path listed.<br>

<strong>Field Courts:</strong><br>
The data revealed that about 50 minors were referred to field courts, as explicitly mentioned in an official letter from the Head of Investigation Branch to the Director of the Directorate. The letter stated:<br>
Brigadier’s recommendation: “Please indicate your decision on referring them to the Military Field Court regardless of their age, as they are minors.”<br>
Director’s response: “They are referred to the Field Court regardless of age.”<br>

<strong>Care Homes:</strong><br>
About 23 children were referred to care homes, described by different terms such as “orphanage,” “care home,” “shelter,” or “social welfare.” Most referrals were made through the governor.<br>
Care homes mentioned in the data include: SOS Children’s Villages, Qudsaya Shelter Center, and Al-Mabara Association.<br>

<strong>Detention for Exchange:</strong><br>
Several records clearly show that some children were held to pressure their relatives to surrender or to be used in prisoner exchange negotiations. 
The data also mentions the deaths of several children, and their involvement in media interviews to serve regime propaganda. 
There were also records of financial support for producing a film focusing on the “children of Islamic extremists.”<br>

<strong>Juvenile Court:</strong><br>
Some children were referred to the Juvenile Court, especially after the issuance of National Security Bureau Circular No. 8/2051 dated 10 June 2016, 
which stated that all detained minors must be referred to the competent Juvenile Court regardless of the severity of their charges.
<br><br>
</div>
""", unsafe_allow_html=True)

with col_chart_6:
    st.markdown("<h4 style='text-align: left;'>6 - Referral Recommendations from Branch Head to Directorate Director</h4>", unsafe_allow_html=True)
    
    if 'Referrals' in df_filtered.columns:
        # Count values from the filtered DataFrame
        bar_counts = df_filtered['Referrals'].value_counts().head(20).sort_values()
        
        if not bar_counts.empty:
            # Prepare labels for the y-axis
            labels = [
                get_display(arabic_reshaper.reshape(f"{cat}"))
                for cat in bar_counts.index
            ]

            # Create the horizontal bar chart
            fig, ax = plt.subplots(figsize=(14, 8))
            bars = ax.barh(labels, bar_counts.values)

            # Add count values to the right of the bars
            for bar in bars:
                width = bar.get_width()
                label_x_pos = width + 7
                ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                        va='center', ha='left', fontsize=16)

            ax.tick_params(axis='y', labelsize=18)
            ax.set_xlabel('')
            ax.set_xticks([])
            ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)

            plt.grid(axis='x', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)
            # CORRECTION: Removed plt.tight_layout() here for better Arabic label display.
            st.pyplot(fig)
        else:
            st.info("No 'Referrals' data for the selected year.")
    else:
        st.warning("Column 'Referrals' not found in the data.")
        


# New Row: Annual Distribution and Excerpts

# CORRECTION: Re-indexed column variables (col18, col19, col20, col21)
# Renamed for clarity: col_left_spacer4, col_chart_9, col_right_spacer4, col_text_8
col_left_spacer4, col_chart_9, col_right_spacer4, col_text_8 = st.columns([1, 4, 1, 4])

with col_chart_9:
    # Title above the chart
    st.markdown("<h3 style='text-align: center;'>9 - Annual Distribution</h3>", unsafe_allow_html=True)

    # Chart
    # Ensure there are valid dates before attempting to group/plot
    if not df_filtered['date_in'].dropna().empty:
        # Filter out invalid dates (NaT) before grouping
        valid_dates_df = df_filtered.dropna(subset=['date_in'])
        
        # Check if there's data for the period
        if not valid_dates_df.empty:
            counts_monthly = valid_dates_df.groupby(valid_dates_df['date_in'].dt.to_period("M")).size()
            counts_monthly.index = counts_monthly.index.to_timestamp()

            fig, ax = plt.subplots(figsize=(16, 8))
            ax.plot(counts_monthly.index, counts_monthly.values, marker='o', color='royalblue')
            ax.set_title(f"Number of Records per Month ({selected_year_str})", fontsize=12)
            ax.set_xlabel("Month", fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            plt.xticks(rotation=60)
            plt.grid(True)
            st.pyplot(fig)
        else:
            st.info(f"No valid 'date_in' records found for {selected_year_str}.")
    else:
        st.info("No valid 'date_in' records in the dataset for charting.")

    # Explanatory text under the chart
    st.markdown(
        """
        <div style='text-align:left;'>
            The chart above shows the temporal distribution of documented detention cases during this period. 
            The analysis reveals important patterns in the frequency of arrests, which peaked in 
            <strong>May 2013</strong>, indicating a significant escalation in detention operations. 
        <br><br>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_text_8:
    st.markdown("<h3 style='text-align: left;'>8 - Excerpts from the Records</h3>", unsafe_allow_html=True)
    st.markdown("""
<div style='text-align: left;'>
    1 - Release the mentioned person and officially assign him to gather information about the children placed in the SOS Children’s Village under the Directorate.<br>
    2 - Letter to the Minister requesting to withhold the names of children placed in shelters and care homes under our supervision.<br>
    3 - Television interview with the child residing in the house of Assistant 1, A. T.<br>
    4 - Referral of the named persons (...) to the Juvenile Court after conducting a televised interview with them to expose to the public the “dirty methods” of the so-called revolution leaders.<br>
    5 - Response from National Security and Al-Rai refusing to end the case of the two girls as they still serve as a serious deterrent to their father.<br>
    6 - Detention of the named woman (...) and her three children to be used later in prisoner exchange negotiations with the militants of Al-Fijah.<br>
    7 - Memorandum regarding baby milk and children’s supplies – approval granted to disburse the funds through the Directorate’s accountant.<br>
    8 - Dismissal of the minor (...) from the groups affiliated with our Directorate and prohibition of issuing him any weapons.
</div><br><br>
""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# Final Row: Entities Mentioned

# CORRECTION: Re-indexed column variables (col22, col23)
# Renamed for clarity: col_final_spacer, col_final_text
col_final_spacer, col_final_text = st.columns([1, 8])

with col_final_text:
    st.markdown("<h3 style='text-align: left;'>10 - Entities Mentioned in the Records</h3>", unsafe_allow_html=True)

    st.markdown("""
<div style='text-align: left; font-size: 14px; line-height: 2;'>
Security Committee in Homs, General Intelligence Directorate, Political Security Branch, Air Force Intelligence Branch in Hama, 
Anti-Narcotics Directorate, National Security Office, Ministry of Justice, Ministry of Interior, Political Directorate, 
Ministry of Social Affairs and Labor, Special Missions Branch, Special Operations Division, Southern Region Branch, 
Northern Region Branch, Central Region Branch, Eastern Region Branch, City Sector Division, Information Branch, 
Military Police Branch in Damascus, Hama Division, Idlib Division, Sweida Division, Airports Battalion, Ground Forces, 
Communications Directorate, Central Bank of Syria, Committee for the Settlement of Events, Committee No. 1/8/1337, 
Special Execution Group, Anti-Money Laundering and Counter-Terrorism Financing Authority, Special Bureau, 
“The Friends” (unclear reference), Security Office of the Fourth Division, Immigration and Passports Directorate, 
Technical Branch, Organizations Division, Unit 17, Military Field Court, Military Public Prosecution, 
Counter-Terrorism Court, Competent Judiciary, Wanted Lists, Chief Prosecutor, Military Judiciary, 
Military Records Directorate, Rural Damascus Governorate, Juvenile Court, Criminal Security Branch, 
Military Police, Minister of Defense, Directorate of Officer Affairs, Investigation Branch, Coastal Division, 
Commander of the Air Force, Counselor, Ba’ath Brigades, Al-Abbasiyeen Hospital, Security Hospital, Intelligence Division, 
Presidential Palace Security Office, Falcons Group, Security Services, Medical Services, Minister of Finance, 
Criminal Security Directorate, Sednaya Prison, General Staff, Fourth Armored Division, Ministry of Interior (Minister’s Office), 
Governor of the Central Bank of Syria, Minister of Social Affairs and Labor, Administrative Bureau Division, 
Internal Security, Al-Manar TV Channel.
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center;font-size:14px;color:gray;'>
Statistical Report from the Investigation Branch and Air Force Intelligence Records on Children — <b>Unforgotten Trace</b> 2025
</p>
<p style='text-align:center;font-size:14px;color:gray;'>• <b>Prepared by:</b> Luay Al-Hammada</p>
<p style='text-align:center;font-size:14px;color:gray;'>• <b>Contact:</b> alhammada.luay@gmail.com</p>

""", unsafe_allow_html=True)



