import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pydeck as pdk
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(
    page_title="Unforgeten trace",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Global CSS for Arabic text and layout
# -------------------------------
st.markdown("""
<style>
body, div, p {
    font-family: 'Tahoma', Arial, sans-serif;
    direction: rtl;
    text-align: right;
}
h3 {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
}
h4 {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 8px;
}
h5 {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 6px;
}
p, li, div {
    font-size: 16px;
    line-height: 1.7;
}
ul {
    padding-right: 20px;
}
.metadata-card h5 {
    font-size: 16px;
    margin: 2px 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load Data
# -------------------------------
url = "https://raw.githubusercontent.com/Luay-alhammada/Unforgeten_trace/main/under_18_8.csv"

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

df = load_data(url)
df['date_in'] = pd.to_datetime(df['date_in'], errors='coerce')
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

# -------------------------------
# Page Title
# -------------------------------
st.markdown("<h4>الأطفال في سجلات فرع تحقيق المخابرات الجوية</h4>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div>
<h4>• <b>الموضوع:</b> الانتهاكات بحق الأطفال (دون سن الـ 18)</h4>
<h4>• <b>الفترة الزمنية:</b> 2011 حتى 2016</h4>
<h4>• <b>العدد الإجمالي:</b> 1600 سجل</h4>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# Layout
# -------------------------------
col1, col2, col4, col3 = st.columns([1, 4, 1, 4])

# -------------------------------
# Filters
# -------------------------------
with col1:
    st.header("Filters")
    years = sorted(df['date_in'].dt.year.dropna().unique().astype(int), reverse=True)
    years_with_all = ['All Years'] + years
    selected_year = st.selectbox("Select Year", years_with_all)

# Filter data based on selection
if selected_year == "All Years":
    df_filtered = df.copy()
else:
    df_filtered = df[df['date_in'].dt.year == selected_year]

# -------------------------------
# Map
# -------------------------------
with col2:
    st.markdown("<h4>1 - أماكن تولد المعتقلين</h4>", unsafe_allow_html=True)
    st.markdown("<div>حوالي 40% من الاسماء تم ذكر اماكن تولدهم</div><br>", unsafe_allow_html=True)

    # Aggregate counts per birthplace
    df_counts = df_filtered.groupby("مكان الولادة").size().reset_index(name="count")
    df_coords = df_filtered.groupby("مكان الولادة")[["lat", "lon"]].first().reset_index()
    df_map = df_counts.merge(df_coords, on="مكان الولادة", how="left")
    df_map = df_map.dropna(subset=["lat", "lon"])

    # Scale radius
    scaler = MinMaxScaler((5, 20))
    df_map["radius"] = scaler.fit_transform(df_map[["count"]])

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
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Birthplace:</b> {مكان الولادة}<br/><b>Cases:</b> {count}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        },
        map_style="light"
    )
    st.pydeck_chart(r)

# -------------------------------
# Introduction Text
# -------------------------------
with col3:
    st.markdown("<h3>مقدمة</h3>", unsafe_allow_html=True)
    st.markdown("""
<div>
بعد انهيار النظام السوري في الثامن من ديسمبر/كانون الأول 2024، سُرّبت مجموعة كبيرة من الوثائق الاستخباراتية الحساسة، من بينها وثائق تعود إلى فرع التحقيق وإدارة المخابرات الجوية. هذه المواد جاءت على شكل مستندات وجداول بيانات (Excel)، وملفات نصية (Word)، وصور، وملفات (PDF)، حيث جرى استخراج المعلومات من الوثائق المصورة ودمجها في قاعدة بيانات متكاملة.

خضعت هذه البيانات لعمليات تنظيف وتصنيف دقيقة، مع التأكيد على أن التحقق من دقة وصحة جميع المعلومات هو عملية دائمة ومستمرة. ويُقدّم هذا التقرير تحليلًا خاصًا بقضية الأطفال دون سن الثامنة عشرة، ليكون جزءًا من سلسلة تحليلات ستُنشر تباعًا وتتناول موضوعات مختلفة من هذه السجلات.

بلغ إجمالي حجم قاعدة البيانات التي تم بناؤها حوالي 100 ألف سطر، يمثل كل سطر نقطة بيانات مستقلة. وقد تم تطبيق تقنيات متعددة لتصفية هذه البيانات والوصول إلى المعلومات ذات الصلة بالأطفال القُصّر. وتشير البيانات الأولية إلى أن 1600 طفل على الأقل قد ورد ذكرهم في هذه السجلات. هذا الرقم لا يمثل العدد الإجمالي، بل يقتصر على ما استطعنا رصده في الوثائق التي تغطي الفترة من 2011 إلى 2016.

 تضمنت السجلات المسربة تصنيفات دقيقة من المصدر، شملت: تاريخ الاعتقال، تاريخ إرسال الإضبارة، تاريخ عودة الإضبارة، تاريخ الإفراج، تاريخ الميلاد، تاريخ الوفاة، الجرم، مقترح العميد رئيس الفرع، وقرار اللواء.
                
في هذا التقرير، يبدأ التحليل من بيانات مكان ولادة المعتقلين، مرورًا بالدوريات التي نفذت عمليات الاعتقال و الفروع الأمنية التي جرى تسليم المعتقلين إليها. كما يتناول انواع المحققين والاقسام واللجان الفاعلة و يستعرض التقرير أيضا طبيعة التهم الموجّهة للمتقلين وما انتهت إليه قضاياهم، ويُختتم بعرض بياني يوضح التوزع الزمني لعدد المعتقلين خلال تلك السنوات ومقتطفات من السجل.
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# Section 2: Arresting Patrols Pie Chart
# -------------------------------
col5, col6, col7, col8 = st.columns([1,4,1,4])

with col8:
    st.markdown("<h4>2- أسماء الدوريات التي قامت بإعتقالهم</h4>", unsafe_allow_html=True)
    st.markdown("<div>كشف تحليل الوثائق المسربة عن وجود حوالي 50 جهة مختلفة تتبع لعدة أجهزة أمنية وعسكرية كانت مسؤولة عن اعتقال وجلب المعتقلين إلى فرع التحقيق التابع لإدارة المخابرات الجوية. الرسم البياني يظهر أول عشر دوريات كانت الأكثر نشاطًا.</div>", unsafe_allow_html=True)
    
    pie_counts = df_filtered['الدورية_التي_جلبته'].value_counts().head(11)
    pie_counts = pie_counts[pie_counts.index != 'no_value']
    legend_labels = [get_display(arabic_reshaper.reshape(f"{cat}")) for cat in pie_counts.index]

    def autopct_counts(pct, all_vals):
        absolute = int(round(pct/100.*sum(all_vals)))
        return str(absolute)

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(pie_counts.values,
           labels=None,
           autopct=lambda pct: autopct_counts(pct, pie_counts.values),
           startangle=90,
           textprops={'fontsize':6})
    ax.legend(legend_labels, loc="center left", bbox_to_anchor=(1.1, 0.5), fontsize=5, frameon=False)
    ax.axis('equal')
    st.pyplot(fig)

# -------------------------------
# Section 3: Investigators & Departments
# -------------------------------
with col6:
    st.markdown("<h4>3 - المحققين والاقسام داخل الفرع</h4>", unsafe_allow_html=True)
    st.markdown("""
<div>
<p>في الفرع، تظهر البيانات وجود تصنيفين للمحققين:</p>
<ul>
<li><strong>الفئة الأولى:</strong> تشمل المحققين الذين لم تُذكر أسماؤهم، بل رموز تشير إليهم (مثل: ث4، ز10، ل2). يُرجح أن هذا الإجراء يهدف إلى الحفاظ على سريتهم، خاصة في ظل دورهم في انتزاع الاعترافات عبر أساليب التعذيب.</li>
<li><strong>الفئة الثانية:</strong> تضم المحققين الذين ذُكرت أسماؤهم الأولى أو الكاملة. في بعض الحالات، أشارت السجلات إلى القسم أو اللجنة المسؤولة عن التحقيق بدلًا من اسم المحقق. من تجربتي في فرع المزة كانت إجراءات التحقيق تبدأ بالضرب والتعذيب في ساحة الفرع لانتزاع الاعترافات، وبعد الاعتراف، نقلت إلى غرفة محقق آخر يجلس خلف مكتبه حيث لعب دور المحقق اللطيف.</li>
</ul>
<p><strong>الرتب العسكرية المشاركة في التحقيقات:</strong></p>
<ul>
<li>مقدم، نقيب , رائد، ملازم، مساعد، عميد، عقيد.</li>
</ul>
<p><strong>الأقسام واللجان الوارد ذكرها في السجلات :</strong></p>
<ul>
<li>قسم التنظيمات والتيارات التكفيرية - قسم التحقيق الجنائي والاقتصادي - قسم التحقيق الأمني ومكافحة الإرهاب - قسم التحقيق الانضباطي والمسلكي.</li>
<li>اللجنة الأولى - اللجنة الثانية - لجنة أولى + لجنة ثانية - لجنة الميدان - لجنة التحقيق مع المعادين.</li>
</ul>
</div>
""", unsafe_allow_html=True)

col9, col10, col11, col12 = st.columns([1,4,1,4])

# Places of Arrest
with col10:
    st.markdown("<h5>5 - أماكن الاعتقال في الجوية</h5>", unsafe_allow_html=True)
    st.markdown("""
<div>
فيما يخص أماكن الاعتقال، أظهرت البيانات ما يقارب أربعين موقعًا للاعتقال أو الاحتجاز. 
يوضح الرسم البياني أعلاه أكثر 15 موقعًا ورودًا، مثل <b>المزة الجديد</b> و<b>المزة القديم</b>. 
كما وردت في البيانات معلومات متفرقة، كأرقام أو أسماء ضباط وأشخاص، تحتاج إلى بحث إضافي للتأكد مما إذا كانت تعكس مواقع فعلية أو أنها أُدرجت بطريق الخطأ.
</div><br>
""", unsafe_allow_html=True)

    bar_counts = df_filtered['Place of Arrest'].value_counts().head(15).sort_values(ascending=False)
    labels = [get_display(arabic_reshaper.reshape(f"{cat}")) for cat in bar_counts.index]

    fig, ax = plt.subplots(figsize=(14,8))
    bars = ax.bar(labels, bar_counts.values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 2, f'{int(height)}', ha='center', va='bottom', fontsize=14)
    ax.tick_params(axis='x', labelsize=16, rotation=45)
    ax.tick_params(axis='y', labelsize=14)
    ax.spines[['top', 'right']].set_visible(False)
    plt.grid(axis='y', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

# Charges
with col12:
    st.markdown("<h4>4 - التهم الموجهة</h4>", unsafe_allow_html=True)
    st.markdown("""
<div>
تم ترتيب التهم من الأكثر تكراراً إلى الأقل، بناءً على البيانات المُقدمة وهذا التهم مشتركة للاطفال والكبار الذين اعتقلو معهم :

1. <b>المشاركة في المظاهرات وأعمال الشغب:</b> تشمل المشاركة في المظاهرات، أعمال الشغب والتخريب، التحريض على التظاهر، مقاومة الدوريات، ترديد شعارات مناهضة للدولة، ورمي الحجارة على قوات الأمن.
2. <b>العضوية في مجموعات إرهابية مسلحة:</b> تشمل الانضمام إلى جماعات مسلحة مختلفة، المشاركة في عمليات إرهابية ضد الجيش والأمن، إقامة حواجز على الطرقات، وحيازة أسلحة.
3. <b>التعامل مع المسلحين:</b> تقديم الدعم المادي واللوجستي للمسلحين، نقل الأسلحة والذخيرة، توفير المأوى، وتقديم المعلومات.
4. <b>التحريض:</b> يشمل التحريض على التظاهر، التحريض الطائفي، وتحريض العسكريين على الانشقاق.
5. <b>الاشتباه بوضعهم الأمني:</b> مراقبة الحواجز والمنشآت الحكومية، حيازة مقاطع مسيئة على الهاتف، وعدم الامتثال لأوامر الدورية.
6. <b>التواصل مع إرهابيين:</b> التواصل مع أفراد معروفين بانتمائهم لجماعات إرهابية، وتبادل المعلومات معهم.
7. <b>مختلف:</b> تشمل سرقة، تزوير، انتحال صفة أمنية، تخريب ممتلكات عامة، محاولة مغادرة البلاد بطريقة غير شرعية.
</div>
""", unsafe_allow_html=True)

# -------------------------------
# Section 7 & 6: Referral Paths & Branch Recommendations
# -------------------------------
col14, col15, col16, col17 = st.columns([1,4,1,4])

# Referral Paths
with col15:
    st.markdown("<h4>7 - مسارات الإحالة</h4>", unsafe_allow_html=True)
    st.markdown("""
<div>
<p>
تُظهر البيانات إحالة الأطفال إلى جهات متعددة. النسبة الأكبر من الإحالات كانت إلى إخلاء السبيل، تليها الإحالة إلى النيابة العامة أو المحكمة العسكرية ومحكمة قضايا الإرهاب. وفي المقابل، لم يُذكر مسار الإحالة لنحو 100 حالة.
</p>
<p><strong>المحاكم الميدانية:</strong></p>
<p>كشفت البيانات عن إحالة ما يقارب 50 حدثًا إلى المحاكم الميدانية، حيث ورد ذلك صراحةً في كتاب موجه من رئيس فرع التحقيق إلى مدير الإدارة. ويُظهر محتوى الكتاب التالي:
اقتراح العميد: "يُرجى بيان قرار سيادتكم حول إحالتهما إلى محكمة الميدان العسكرية بغض النظر عن سنه كونه حدثًا."
جواب مدير الإدارة: يحال إلى محكمة الميدان بغض النظر عن سنه.
</p>
<p><strong>التحفظ للمبادلة:</strong></p>
<p>كشفت العديد من السجلات عن التحفظ على الأطفال صراحةً، إما للضغط على ذويهم لتسليم أنفسهم أو لاستخدامهم في مفاوضات التبادل. أظهرت السجلات أيضًا وفاة عدد من الأطفال، وأيضا إلى إجراء مقابلات مع صحف وتلفزيونات محلية وعربية ودولية لتعزيز بروباغندا النظام.
وتكشف السجلات أيضًا عن وجود دعم مالي لإنتاج فيلم يركز على دور "أطفال المتطرفين الإسلاميين".
</p>
<p><strong>محكمة الأحداث:</strong></p>
<p>بعض الأطفال تمت إحالتهم إلى محكمة الأحداث خصوصًا بعد صدور تعميم مكتب الأمن الوطني رقم 8/2051 تاريخ 2016/6/10 يقضي بإحالة كافة الموقوفين الأحداث إلى محكمة الأحداث المختصة حكمًا مهما بلغت درجة الجرمية.</p>
""", unsafe_allow_html=True)

# Branch Recommendations
with col17:
    st.markdown("<h4>6 - مقترحات الاحالة من رئيس الفرع لمدير الادارة</h4>", unsafe_allow_html=True)
    bar_counts = df_filtered['احالات'].value_counts().head(20).sort_values()
    labels = [get_display(arabic_reshaper.reshape(f"{cat}")) for cat in bar_counts.index]

    fig, ax = plt.subplots(figsize=(14,8))
    bars = ax.barh(labels, bar_counts.values)
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 7, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center', ha='left', fontsize=16)
    ax.tick_params(axis='y', labelsize=18)
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.spines[['top','right','bottom','left']].set_visible(False)
    plt.grid(axis='x', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

# -------------------------------
# Section 8 & 9: Yearly Distribution & Record Excerpts
# -------------------------------
col18, col19, col20, col21 = st.columns([1,4,1,4])

# Yearly Distribution
with col19:
    st.markdown("<h3> 9 - التوزع السنوي</h3>", unsafe_allow_html=True)
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

    st.markdown("""
<div>
يُظهر المخطط أعلاه التوزيع الزمني لحالات الاعتقال الموثقة خلال هذه الفترة، مع ذروة في شهر <strong>أيار 2013</strong>.
</div>
""", unsafe_allow_html=True)

# Record Excerpts
with col21:
    st.markdown("<h3> 8 - مقتطفات من السجل</h3>", unsafe_allow_html=True)
    st.markdown("""
<div>
    <li>إخلاء سبيل المذكور وربطه بشكل رسمي لتقصي اخبار الاطفال المودعين لدى الادارة في قرية الاطفال sos</li>
    <li>كتاب الى الوزيره لحجب اسماء الاطفال المودعين لصالحنا في مراكز الايواء ودور الرعاية</li>
    <li>مقابله تلفزيونية مع الطفل الموجود في منزل المساعد1 ع ت</li>
    <li>إحالة المدعوين ( ـــ ـــ ) الى محكمة الاحداث بعد إجراء مقابلة تلفزيونية معهم لكشف الوسائل القذرة لقادة الثورة المزعومة للرأي العام الداخلي والخارجي</li>
    <li>إجابة الامن الوطني مع الراي بعدم الموافقة على انهاء وضع الطفلتين لانهما لا تزالا تشكلان عامل رادع جدي لوالدهما</li>
    <li>التحفظ على المدعوين ( ـ ـ وأطفالها الثلاثة ) للإستفادة منهم في إحدى عمليات المبادلة والتفاوض مع مسلحي الفيجة</li>
    <li>مذكرة عرض بخصوص حليب اطفال ومستلزمات اطفال\nالموافقة على صرف المبلغ ع/ط محاسب الادارة</li>
    <li>فصل الحدث ... من المجموعات التابعة لادارتنا وعدم تسليمه اي سلاح</li>
</div><br>
""", unsafe_allow_html=True)

col22, col23 = st.columns([1,8])

with col23:
    st.markdown("<h3>الجهات الوارد ذكرها في السجلات</h3>", unsafe_allow_html=True)
    st.markdown("""
<div>
اللجنة الأمنية بحمص، إدارة المخابرات العامة، شعبة الأمن السياسي، قسم المخابرات الجوية بحماه، إدارة مكافحة المخدرات، مكتب الأمن الوطني، وزارة العدل، وزارة الداخلية، الإدارة السياسية، وزارة الشؤون الاجتماعية والعمل، فرع المهام الخاصة، قسم العمليات الخاصة، فرع المنطقة الجنوبية، فرع المنطقة الشمالية، فرع المنطقة الوسطى، فرع المنطقة الشرقية، قسم قطاع المدينة، فرع المعلومات، فرع الشرطة العسكرية بدمشق، قسم حماه، قسم إدلب، قسم السويداء، كتيبة المطارات، القوات العاملة على الأرض، إدارة الاتصالات، مصرف سوريا المركزي، اللجنة الخاصة بتسوية أوضاع المتورطين بالأحداث، اللجنة المشكلة بالرقم 1/8/1337، مجموعة التنفيذ الخاصة، هيئة مكافحة غسيل الأموال وتمويل الإرهاب، الديوان الخاص، الأصدقاء (إشارة غامضة)، مكتب الأمن بالفرقة الرابعة، إدارة الهجرة والجوازات، الفرع الفني، قسم التنظيمات، الوحدة 17، محكمة الميدان العسكرية، النيابة العامة العسكرية، محكمة قضايا الإرهاب، القضاء المختص، لوائح المطلوبين، المحامي العام الأول، القضاء العسكري، إدارة السجلات العسكرية، محافظة ريف دمشق، محكمة الأحداث، فرع الأمن الجنائي، الشرطة العسكرية، وزير الدفاع، إدارة شؤون الضباط، فرع التحقيق، قسم الساحلية، السيد اللواء قائد القوى الجوية، المستشار، كتائب البعث، مشفى العباسيين، مشفى أمن، شعبة المخابرات، مكتب أمن القصر، مجموعة الصقور، الأجهزة الأمنية، الخدمات الطبية، وزير المالية، إدارة الأمن الجنائي، سجن صيدنايا، هيئة الأركان، الفرقة الرابعة دبابات، وزارة الداخلية (مكتب الوزير)، حاكم مصرف سوريا المركزي، وزيرة الشؤون الاجتماعية والعمل، قسم ديوان الإدارة، الأمن الداخلي، قناة المنار.
</div><br>
""", unsafe_allow_html=True)

# -------------------------------
# Footer
# -------------------------------
st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center;font-size:14px;color:gray;'>
تقرير إحصائي من سجلات فرع التحقيق والمخابرات الجوية حول الأطفال <b>Unforgeten Trace</b> 2025
</p>
<p style='text-align:center;font-size:14px;color:gray;'>• <b>إعداد:</b> لؤي الحمادة</p>
<p style='text-align:center;font-size:14px;color:gray;'>• <b>للتواصل:</b> alhammada.luay@gmail.com</p>
""", unsafe_allow_html=True)


