import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(
    page_title="Unforgeten trace",        # optional
    page_icon="📊",             # optional
    layout="wide",              # 👈 this makes wide mode default
    initial_sidebar_state="expanded"  # optional
)
url = "https://raw.githubusercontent.com/Luay-alhammada/Unforgeten_trace/main/under_18_8.csv"

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# Load Data
df = load_data(url)
df['date_in'] = pd.to_datetime(df['date_in'], errors='coerce')

# -------------------------------
# Page Title
# -------------------------------
st.markdown("<h4 style='text-align: center; direction: rtl;'>الأطفال في سجلات فرع تحقيق المخابرات الجوية</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True) # Adds a line break for spacing

st.markdown("""
<div style='text-align: right; direction: rtl;'>
<h4 style='text-align: right;'>• <b>الموضوع:</b> الانتهاكات بحق الأطفال (دون سن الـ 18)</h4>
<h4 style='text-align: right;'>• <b>الفترة الزمنية:</b> 2011 حتى 2016</h4>
<h4 style='text-align: right;'>• <b>العدد الإجمالي:</b> 1600 سجل</h4>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True) # Adds a line break for spacing


# -------------------------------
# Layout: Left (Filters), Middle (Chart), Right (Pie Chart)
# -------------------------------
col1, col2,col4, col3 = st.columns([1, 4,1, 4])  # 1:4:4 ratio

# -------------------------------
# Left Column: Filters
# -------------------------------
with col1:
    st.header("Filters")
    years = sorted(df['date_in'].dt.year.dropna().unique().astype(int), reverse=True)
    years_with_all = ['All Years'] + years
    selected_year = st.selectbox("Select Year", years_with_all)

# Step 2: Filter the DataFrame based on the selection
if selected_year == "All Years":
    df_filtered = df.copy()
else:
    df_filtered = df[df['date_in'].dt.year == selected_year]

# -------------------------------
# Middle Column: Line Chart
# -------------------------------
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pydeck as pdk

# Load data
ur11 = "https://raw.githubusercontent.com/Luay-alhammada/Unforgeten_trace/refs/heads/main/%D9%85%D9%83%D8%A7%D9%86_%D8%A7%D9%84%D9%88%D9%84%D8%A7%D8%AF%D8%A9.csv"

# Load Data
df_birthplace = load_data(url1)

# Ensure lat/lon are numeric
df_birthplace["lat"] = df_birthplace.to_numeric(df_birthplace["lat"], errors="coerce")
df_birthplace["lon"] = df_birthplace.to_numeric(df_birthplace["lon"], errors="coerce")

# Define radius for scatter plot (in pixels for constant size)
scaler = MinMaxScaler((5, 20))
df_birthplace["radius"] = scaler.fit_transform(df_birthplace[["count"]])

# Define scatter layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_birthplace,
    get_position=["lon", "lat"],
    get_radius="radius",
    get_fill_color=[200, 30, 0, 160],
    pickable=True,
    radius_units="pixels",
)

# View centered on Syria
view_state = pdk.ViewState(latitude=34.8, longitude=38, zoom=6)

# Create the Deck object with the customized tooltip
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>Birthplace:</b> {مكان الولادة}<br/><b>Cases:</b> {count}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white"
        }
    },
    map_style="light"  # This is the key change
)

# The rest of your Streamlit layout code goes here
with col2:
    st.markdown("<h4 style='text-align: right; direction: rtl;'>1 -أماكن تولد المعتقلين </h4>", unsafe_allow_html=True)
    st.markdown("""
<div dir='rtl' style='text-align: right; font-size: 16px;'>
حوالي 40% من الاسماء تم ذكر اماكن تولدهم</div><br>
""", unsafe_allow_html=True)

    st.pydeck_chart(r)




# -------------------------------
with col3:
    st.markdown("<h3 style='text-align: right; direction: rtl;'>مقدمة</h3>", unsafe_allow_html=True)
    st.markdown("""
<div style='direction: rtl;'>
بعد انهيار النظام السوري في الثامن من ديسمبر/كانون الأول 2024، سُرّبت مجموعة كبيرة من الوثائق الاستخباراتية الحساسة، من بينها وثائق تعود إلى فرع التحقيق وإدارة المخابرات الجوية. هذه المواد جاءت على شكل مستندات وجداول بيانات (Excel)، وملفات نصية (Word)، وصور، وملفات (PDF)، حيث جرى استخراج المعلومات من الوثائق المصورة ودمجها في قاعدة بيانات متكاملة.

خضعت هذه البيانات لعمليات تنظيف وتصنيف دقيقة، مع التأكيد على أن التحقق من دقة وصحة جميع المعلومات هو عملية دائمة ومستمرة. ويُقدّم هذا التقرير تحليلًا خاصًا بقضية الأطفال دون سن الثامنة عشرة، ليكون جزءًا من سلسلة تحليلات ستُنشر تباعًا وتتناول موضوعات مختلفة من هذه السجلات.

بلغ إجمالي حجم قاعدة البيانات التي تم بناؤها حوالي 100 ألف سطر، يمثل كل سطر نقطة بيانات مستقلة. وقد تم تطبيق تقنيات متعددة لتصفية هذه البيانات والوصول إلى المعلومات ذات الصلة بالأطفال القُصّر. وتشير البيانات الأولية إلى أن 1600 طفل على الأقل قد ورد ذكرهم في هذه السجلات. هذا الرقم لا يمثل العدد الإجمالي، بل يقتصر على ما استطعنا رصده في الوثائق التي تغطي الفترة من 2011 إلى 2016.

 تضمنت السجلات المسربة تصنيفات دقيقة من المصدر، شملت: تاريخ الاعتقال، تاريخ إرسال الإضبارة، تاريخ عودة الإضبارة، تاريخ الإفراج، تاريخ الميلاد، تاريخ الوفاة، الجرم، مقترح العميد رئيس الفرع، وقرار اللواء.
                
في هذا التقرير، يبدأ التحليل من بيانات مكان ولادة المعتقلين، مرورًا بالدوريات التي نفذت عمليات الاعتقال و الفروع الأمنية التي جرى تسليم المعتقلين إليها. كما يتناول انواع المحققين والاقسام واللجان الفاعلة و يستعرض التقرير أيضا طبيعة التهم الموجّهة للمتقلين وما انتهت إليه قضاياهم، ويُختتم بعرض بياني يوضح التوزع الزمني لعدد المعتقلين خلال تلك السنوات ومقتطفات من السجل.

</div>
""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    

# --- Start of New Section ---

#st.markdown("<hr>", unsafe_allow_html=True) # Adds a horizontal line for separation

# Create a new row of columns with the same ratio
col5, col6, col7, col8 = st.columns([1, 4, 1, 4])

# Add content to the new columns
# with col5:
#     st.header("New Filters")
#     st.write("This is a new filter column.")

with col8:
    st.markdown("<h4 style='text-align: right; direction: rtl;'>2- أسماء الدوريات التي قامت بإعتقالهم</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div style='direction: rtl;'>
      كشف تحليل الوثائق المسربة عن وجود حوالي 50 جهة مختلفة تتبع لعدة أجهزة أمنية وعسكرية كانت مسؤولة عن اعتقال وجلب المعتقلين إلى فرع التحقيق التابع لإدارة المخابرات الجوية. الرسم البياني يظهر أول عشر دوريات كانت الأكثر نشاطًا.
    </div>
    """, unsafe_allow_html=True)
    
    # Get the top 11 categories and their counts
    pie_counts = df_filtered['الدورية_التي_جلبته'].value_counts().head(11)

    # Exclude the 'no_value' category
    pie_counts = pie_counts[pie_counts.index != 'no_value']

    # Prepare legend labels with Arabic reshaping
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
    st.pyplot(fig)

with col6:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: right; direction: rtl; margin-bottom: 5px;'>3 -  المحققين والاقسام داخل الفرع</h4>", unsafe_allow_html=True)
    st.markdown("""
<div style='direction: rtl;'>
    <p style='margin: 0; padding: 0;'>في الفرع، تظهر البيانات وجود تصنيفين للمحققين:</p>
    <ul style='margin-top: 5px; padding-right: 20px;'>
        <li>
            <strong>الفئة الأولى:</strong>
تشمل المحققين الذين لم تُذكر أسماؤهم، بل رموز تشير إليهم (مثل: ث4، ز10، ل2). يُرجح أن هذا الإجراء يهدف إلى الحفاظ على سريتهم، خاصة في ظل دورهم في انتزاع الاعترافات عبر أساليب التعذيب</li>
        <li>
            <strong>الفئة الثانية:</strong>  تضم المحققين الذين ذُكرت أسماؤهم الأولى أو الكاملة. في بعض الحالات، أشارت السجلات إلى القسم أو اللجنة المسؤولة عن التحقيق بدلًا من اسم المحقق<br>
                من تجربتي في فرع المزة كانت إجراءات التحقيق تبدأ بالضرب والتعذيب في ساحة الفرع لانتزاع الاعترافات. وبعد الاعتراف، نقلت إلى غرفة محقق أخر يجلس خلف مكتبه حيث لعب دور المحقق اللطيف
        </li>
    </ul>
    <br>
    <p style='margin: 0; padding: 0;'><strong> الرتب العسكرية المشاركة في التحقيقات:</strong></p>
    <ul style='margin-top: 5px; padding-right: 20px;'>
        <li>مقدم، نقيب , رائد، ملازم، مساعد، عميد، عقيد.</li>
    </ul>
    <br>
    <p style='margin: 0; padding: 0;'><strong>الأقسام واللجان الوارد ذكرها في السجلات :</strong></p>
    <ul style='margin-top: 5px; padding-right: 20px;'>
        <li>
            <p style='margin: 0; padding: 0;'>قسم التنظيمات والتيارات التكفيرية - قسم التحقيق الجنائي والاقتصادي - قسم التحقيق الأمني ومكافحة الإرهاب - قسم التحقيق الانضباطي والمسلكي.</p>
        </li>
        <li>
            <p style='margin: 0; padding: 0;'>اللجنة الأولى - اللجنة الثانية - لجنة أولى + لجنة ثانية - لجنة الميدان - لجنة التحقيق مع المعادين.</p><br><br>
        </li>
    </ul>
</div>
""", unsafe_allow_html=True)


col9, col10, col11, col12 = st.columns([1, 4, 1, 4])

with col10:
    st.markdown("<h5 style='text-align: right; direction: rtl;'>5 - أماكن الاعتقال في الجوية</h5>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='direction: rtl; text-align: right; font-size: 18px; line-height: 1.8;'>
        فيما يخص أماكن الاعتقال، أظهرت البيانات ما يقارب أربعين موقعًا للاعتقال أو الاحتجاز. 
        يوضح الرسم البياني أعلاه أكثر 15 موقعًا ورودًا، مثل <b>المزة الجديد</b> و<b>المزة </b> (الذي يُشار إليه غالبًا بالقديم). 
        في هذا المكان تحديدًا تم الزج بي.
        <br>
        كما وردت في البيانات معلومات متفرقة، كأرقام أو أسماء ضباط وأشخاص، تحتاج إلى بحث إضافي للتأكد مما إذا كانت تعكس مواقع فعلية 
        أو أنها أُدرجت بطريق الخطأ.
        </div><br>
        """,
        unsafe_allow_html=True
    )
    
    # Count values from the filtered DataFrame
    bar_counts = df_filtered['Place of Arrest'].value_counts().head(15).sort_values(ascending=False)

    # Prepare labels for the x-axis
    labels = [
        get_display(arabic_reshaper.reshape(f"{cat}"))
        for cat in bar_counts.index
    ]

    # Create the vertical bar chart
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.bar(labels, bar_counts.values)

    # Add the value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2, f'{int(height)}', 
                ha='center', va='bottom', fontsize=14)

    # Rotate x-axis labels so Arabic text fits
    ax.tick_params(axis='x', labelsize=16, rotation=45, labelrotation=45)
    ax.tick_params(axis='y', labelsize=14)

    # Remove spines for a cleaner look
    ax.spines[['top', 'right']].set_visible(False)

    # Add horizontal gridlines
    plt.grid(axis='y', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)

    # Tight layout and show
    plt.tight_layout()
    st.pyplot(fig)







with col12:
    st.markdown("<h4 style='text-align: right; direction: rtl;'> 4 - التهم الموجهة</h4>", unsafe_allow_html=True)

    st.markdown("""
<div dir='rtl' style='text-align: right; font-size: 16px;'>
تم ترتيب التهم من الأكثر تكراراً إلى الأقل، بناءً على البيانات المُقدمة وهذا التهم مشتركة للاطفال والكبار الذين اعتقلو معهم :

1. <b>المشاركة في المظاهرات وأعمال الشغب:</b> تشمل هذه التهم المشاركة في المظاهرات، أعمال الشغب والتخريب، التحريض على التظاهر، مقاومة الدوريات، ترديد شعارات مناهضة للدولة، ورمي الحجارة على قوات الأمن. تتضمن بعض الحالات حمل لافتات مسيئة، أعلام، وكتابة عبارات مسيئة على الجدران.
2. <b>العضوية في مجموعات إرهابية مسلحة:</b> تشمل هذه التهم الانضمام إلى جماعات مسلحة مختلفة، المشاركة في عمليات إرهابية ضد الجيش والأمن، إقامة حواجز على الطرقات، وحيازة أسلحة.
3. <b>التعامل مع المسلحين:</b> تشمل هذه التهم تقديم الدعم المادي واللوجستي للمسلحين، نقل الأسلحة والذخيرة، توفير المأوى، وتقديم المعلومات.
4. <b>التحريض:</b> يشمل التحريض على التظاهر، التحريض الطائفي، وتحريض العسكريين على الانشقاق.
5. <b>الاشتباه بوضعهم الأمني:</b> تشمل هذه التهم مراقبة الحواجز والمنشآت الحكومية، حيازة مقاطع مسيئة على الهاتف، وعدم الامتثال لأوامر الدورية.
6. <b>التواصل مع إرهابيين:</b> تشمل هذه التهم التواصل مع أفراد معروفين بانتمائهم لجماعات إرهابية، وتبادل المعلومات معهم.
7. <b>مختلف:</b> تشمل هذه الفئة تهمًا متفرقة مثل سرقة، تزوير، انتحال صفة أمنية، تخريب ممتلكات عامة، محاولة مغادرة البلاد بطريقة غير شرعية.
</div>
""", unsafe_allow_html=True)
    

col14,col15, col16,col17 = st.columns([ 1,4,1, 4])

with col15:

    st.markdown("<h4 style='text-align: right; direction: rtl;'> 7 -  مسارات الإحالة </h4>", unsafe_allow_html=True)
    st.markdown("""
<div style='direction: rtl;'>
    تُظهر البيانات إحالة الأطفال إلى جهات متعددة. النسبة الأكبر من
     الإحالات كانت إلى إخلاء السبيل، تليها الإحالة إلى النيابة العامة أو المحكمة العسكرية ومحكمة قضايا الإرهاب. وفي المقابل، لم يُذكر مسار الإحالة لنحو 100 حالة.<br>
    <strong> المحاكم الميدانية</strong> :<br>
    كشفت البيانات عن إحالة ما يقارب 50 حدثًا إلى المحاكم الميدانية، حيث ورد ذلك صراحةً في كتاب موجه من رئيس فرع التحقيق إلى مدير الإدارة. ويُظهر محتوى الكتاب التالي:<br>
    اقتراح العميد: "يُرجى بيان قرار سيادتكم حول إحالتهما إلى محكمة الميدان العسكرية بغض النظر عن سنه كونه حدثًا."<br>
     جواب مدير الإدارة : يحال الى محكمة الميدان بغض النظر عن سنه <br>
    <strong> دور الرعاية</strong> :<br>
     أُحيل نحو 23 طفلًا إلى دور الرعاية، حيث وردت مصطلحات مختلفة لذلك، مثل "ميتم"، "دار رعاية"، "ملجأ"، أو "الرعاية الاجتماعية". وكانت معظم هذه الإحالات تتم عن طريق المحافظ.
    <br>أسماء دور الرعاية التي وردت في البيانات :<br> 
    قرى الاطفال SOS , مركز ايواء ضاحية قدسيا- جمعية المبرة <br>
    <strong> التحفظ للمبادلة:</strong> :<br>
     كشفت العديد من السجلات عن التحفظ على الأطفال صراحةً، إما للضغط على ذويهم لتسليم أنفسهم أو لاستخدامهم في مفاوضات التبادل. أظهرت السجلات أيضا وفاة عدد من 
    الأطفال، وأيضا إلى إجراء مقابلات مع صحف وتلفزيونات محلية وعربية ودولية لتعزيز بروباغاندا النظام.
     وتكشف السجلات أيضًا عن وجود دعم مالي لإنتاج فيلم يركز على دور "أطفال المتطرفين الإسلاميين".
 <br>
    <strong> محكمة الاحداث</strong> :<br>
    بعض الاطفال تمت احالتهم الى محكمة الاحداث خصوصا بعد صدور تعميم مكتب الامن الوطني رقم 8/2051 تاريخ 
    2016/6/10 يقضي باحالة كافة الموقوفين الاحداث الى محكمة الاحداث المختصة حكما مهما بلغت درجة الجرمية <br><br>
</div>
""", unsafe_allow_html=True)

with col17:
    st.markdown("<h4 style='text-align: right; direction: rtl;'> 6 - مقترحات الاحالة من رئيس الفرع لمدير الادارة</h4>", unsafe_allow_html=True)
    
    # Count values from the filtered DataFrame
    bar_counts = df_filtered['احالات'].value_counts().head(20).sort_values()
    
    # Prepare labels for the y-axis
    labels = [
        get_display(arabic_reshaper.reshape(f"{cat}"))
        for cat in bar_counts.index
    ]

    # Create the horizontal bar chart figure and axes
    fig, ax = plt.subplots(figsize=(14, 8))

    # Create the horizontal bar chart
    bars = ax.barh(labels, bar_counts.values)

    # Add the value labels to the end of each bar
    for bar in bars:
        width = bar.get_width()
        label_x_pos = width + 7  # Adjust this value to add spacing
        ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center', ha='left', fontsize=16)

    # Set the font size for the y-axis (bar names) labels
    ax.tick_params(axis='y', labelsize=18)
    
    # Remove the x-axis title and values
    ax.set_xlabel('')
    ax.set_xticks([])
    
    # Remove the rectangular frame around the plot
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    
    # Customize and keep the vertical gridlines
    plt.grid(axis='x', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)

    # Show the chart first
    plt.tight_layout()
    st.pyplot(fig)




col18,col19, col20,col21 = st.columns([ 1,4,1, 4])

with col19:
    # Title above the chart
    st.markdown("<h3 style='text-align: center; direction: rtl;'>التوزع السنوي</h3>", unsafe_allow_html=True)

    # Chart
    counts_monthly = df_filtered.groupby(df_filtered['date_in'].dt.to_period("M")).size()
    counts_monthly.index = counts_monthly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(16,8))
    ax.plot(counts_monthly.index, counts_monthly.values, marker='o', color='royalblue')
    ax.set_title(f"Number of Records per Month ({selected_year})", fontsize=12)
    ax.set_xlabel("Month", fontsize=10)
    ax.set_ylabel("Count", fontsize=10)
    plt.xticks(rotation=60)
    plt.grid(True)
    st.pyplot(fig)

    # Explanatory text under the chart
    st.markdown(
        """
        <div style='direction: rtl; text-align:right;'>
            يُظهر المخطط البياني أعلاه التوزيع الزمني لحالات الاعتقال الموثقة خلال هذه الفترة. 
            ويكشف التحليل عن أنماط مهمة في وتيرة الاعتقالات، حيث وصلت إلى ذروتها في شهر 
            <strong>أيار من عام 2013</strong>، مما يشير إلى تصعيد كبير في عمليات الاعتقال. 
        <br><br>
        </div>
        """,
        unsafe_allow_html=True
    )

with col21:
    st.markdown("<h3 style='text-align: right; direction: rtl;'>مقتطفات من السجل</h3>", unsafe_allow_html=True)
    st.markdown("""
<div style='direction: rtl;'>
    1 -إخلاء سبيل المذكور وربطه بشكل رسمي لتقصي اخبار الاطفال المودعين لدى الادارة في قرية الاطفال sos<br>
    2 - كتاب الى الوزيره لحجب اسماء الاطفال المودعين لصالحنا في مراكز الايواء ودور الرعاية<br>
    3 - مقابله تلفزيونية مع الطفل الموجود في منزل المساعد1  ع ت <br>
    4 - إحالة المدعوين (  ـــ  ـــ  ) الى محكمة الاحداث بعد إجراء مقابلة تلفزيونية معهم لكشف الوسائل القذرة لقادة الثورة المزعومة للرأي العام الداخلي والخارجي <br>
    5 - إجابة الامن الوطني مع الراي بعدم الموافقة على انهاء وضع الطفلتين لانهما لا تزالا تشكلان عامل رادع جدي لوالدهما <br>
    6 -التحفظ على المدعوين ( ـ  ـ  وأطفالها الثلاثة ) للإستفادة منهم في إحدى عمليات المبادلة والتفاوض مع مسلحي الفيجة <br>
    7 - مذكرة عرض بخصوص حليب اطفال ومستلزمات اطفال\nالموافقة على صرف المبلغ ع/ط محاسب الادارة <br>
    8 - فصل الحدث ... من المجموعات التابعة لادارتنا وعدم تسليمه اي سلاح

</div><br><br>
""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)



col22, col23, = st.columns([1,8])

with col23:
    st.markdown("<h3 style='text-align: right; direction: rtl;'>الجهات الوارد ذكرها في السجلات</h3>", unsafe_allow_html=True)

    st.markdown("""
<div style='direction: rtl; text-align: right; font-size: 14px; line-height: 2;'>
اللجنة الأمنية بحمص، إدارة المخابرات العامة، شعبة الأمن السياسي، قسم المخابرات الجوية بحماه، إدارة مكافحة المخدرات، مكتب الأمن الوطني، وزارة العدل، وزارة الداخلية، الإدارة السياسية، وزارة الشؤون الاجتماعية والعمل، فرع المهام الخاصة، قسم العمليات الخاصة، فرع المنطقة الجنوبية، فرع المنطقة الشمالية، فرع المنطقة الوسطى، فرع المنطقة الشرقية، قسم قطاع المدينة، فرع المعلومات، فرع الشرطة العسكرية بدمشق، قسم حماه، قسم إدلب، قسم السويداء، كتيبة المطارات، القوات العاملة على الأرض، إدارة الاتصالات، مصرف سوريا المركزي، اللجنة الخاصة بتسوية أوضاع المتورطين بالأحداث، اللجنة المشكلة بالرقم 1/8/1337، مجموعة التنفيذ الخاصة، هيئة مكافحة غسيل الأموال وتمويل الإرهاب، الديوان الخاص، الأصدقاء (إشارة غامضة)، مكتب الأمن بالفرقة الرابعة، إدارة الهجرة والجوازات، الفرع الفني، قسم التنظيمات، الوحدة 17، محكمة الميدان العسكرية، النيابة العامة العسكرية، محكمة قضايا الإرهاب، القضاء المختص، لوائح المطلوبين، المحامي العام الأول، القضاء العسكري، إدارة السجلات العسكرية، محافظة ريف دمشق، محكمة الأحداث، فرع الأمن الجنائي، الشرطة العسكرية، وزير الدفاع، إدارة شؤون الضباط، فرع التحقيق، قسم الساحلية، السيد اللواء قائد القوى الجوية، المستشار، كتائب البعث، مشفى العباسيين، مشفى أمن، شعبة المخابرات، مكتب أمن القصر، مجموعة الصقور، الأجهزة الأمنية، الخدمات الطبية، وزير المالية، إدارة الأمن الجنائي، سجن صيدنايا، هيئة الأركان، الفرقة الرابعة دبابات، وزارة الداخلية (مكتب الوزير)، حاكم مصرف سوريا المركزي، وزيرة الشؤون الاجتماعية والعمل، قسم ديوان الإدارة، الأمن الداخلي، قناة المنار
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)






