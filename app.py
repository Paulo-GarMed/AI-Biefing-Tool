import streamlit as st
import pycountry
import requests
from openai import OpenAI
import pandas as pd


st.set_page_config(
    page_title="Country Risk Briefing Tool",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 AI-Powered Country Risk Briefing Tool")

st.write(
    "Generate economic and geopolitical risk briefings using real-world data."
)

# COUNTRY LIST
country_objects = sorted(pycountry.countries, key=lambda x: x.name)
country_names = [country.name for country in country_objects]

selected_country = st.selectbox(
    "Select a Country",
    country_names
)

# GET ISO CODE
country_obj = pycountry.countries.get(name=selected_country)
country_code = country_obj.alpha_3

# WORLD BANK API FUNCTION
def get_world_bank_indicator(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=60"

    response = requests.get(url)
    data = response.json()

    try:
        for item in data[1]:
            if item["value"] is not None:
                return round(item["value"], 2), item["date"]
    except:
        return None, None


def get_world_bank_history(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=100"

    response = requests.get(url)
    data = response.json()

    records = []

    try:
        for item in data[1]:
            if item["value"] is not None:
                records.append({
                    "Year": int(item["date"]),
                    "Value": round(item["value"], 2)
                })

        df = pd.DataFrame(records)
        df = df.sort_values("Year")

        return df

    except:
        return pd.DataFrame()


# INDICATORS
# INDICATORS
gdp_growth, gdp_year = get_world_bank_indicator(
    country_code,
    "NY.GDP.MKTP.KD.ZG"
)

inflation, inflation_year = get_world_bank_indicator(
    country_code,
    "FP.CPI.TOTL.ZG"
)

unemployment, unemployment_year = get_world_bank_indicator(
    country_code,
    "SL.UEM.TOTL.ZS"
)

st.subheader(f"Country Selected: {selected_country}")

st.header("Key Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if gdp_growth is not None:
        st.metric("GDP Growth", f"{gdp_growth}%")
        st.caption(f"Latest year: {gdp_year}")
    else:
        st.metric("GDP Growth", "No Data")

with col2:
    if inflation is not None:
        st.metric("Inflation", f"{inflation}%")
        st.caption(f"Latest year: {inflation_year}")
    else:
        st.metric("Inflation", "No Data")

with col3:
    if unemployment is not None:
        st.metric("Unemployment", f"{unemployment}%")
        st.caption(f"Latest year: {unemployment_year}")
    else:
        st.metric("Unemployment", "No Data")

with col4:
    st.metric("Risk Level", "Pending AI")







# -----------------------------------
# AI COUNTRY BRIEF
# -----------------------------------
client = OpenAI(api_key="OPENAI_API_KEY")

st.header("AI Country Risk Brief")

prompt = f"""
Provide a short geopolitical and economic risk analysis for {selected_country}.

Include:
- Economic outlook
- Political stability
- Major risks
- Relationship with the United States

Keep it concise and professional.
"""

try:

    with st.spinner("Generating AI Risk Brief..."):

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a geopolitical risk analyst."},
                {"role": "user", "content": prompt}
            ]
        )

        ai_brief = response.choices[0].message.content

    st.write(ai_brief)

except Exception as e:

    st.error(f"Error generating AI brief: {e}")



st.subheader("Latest Developments")


gnews_api_key = "ebc2c7852f3a58956fe52d88cff6d9a3"

news_url = f"https://gnews.io/api/v4/search?q={selected_country}&lang=en&max=5&apikey={gnews_api_key}"

news_response = requests.get(news_url)
news_data = news_response.json()

try:

    articles = news_data["articles"]

    for article in articles:

        st.markdown(f"### [{article['title']}]({article['url']})")

        st.write(article["description"])

        st.write("---")

except:

    st.write("No recent news found.")



# Simple risk logic

risk_score = 0

if inflation > 8:
    risk_score += 2
elif inflation > 4:
    risk_score += 1

if unemployment > 10:
    risk_score += 2
elif unemployment > 6:
    risk_score += 1

if gdp_growth < 0:
    risk_score += 2
elif gdp_growth < 2:
    risk_score += 1

# Risk classification

if risk_score <= 1:
    risk_level = "Low Risk"
    risk_color = "green"

elif risk_score <= 3:
    risk_level = "Moderate Risk"
    risk_color = "orange"

else:
    risk_level = "High Risk"
    risk_color = "red"

st.markdown(f"""
## Country Risk Level:
### :{risk_color}[{risk_level}]
""")

# Sample trend chart data

trend_data = pd.DataFrame({
    "Indicator": ["GDP Growth", "Inflation", "Unemployment"],
    "Value": [gdp_growth, inflation, unemployment]
})

st.subheader("Economic Indicators Overview")

st.bar_chart(
    trend_data.set_index("Indicator")
)


st.subheader("Historical Economic Trends")

gdp_history = get_world_bank_history(country_code, "NY.GDP.MKTP.KD.ZG")
inflation_history = get_world_bank_history(country_code, "FP.CPI.TOTL.ZG")
unemployment_history = get_world_bank_history(country_code, "SL.UEM.TOTL.ZS")

st.write("GDP Growth Over Time")
st.line_chart(gdp_history.set_index("Year"))

st.write("Inflation Over Time")
st.line_chart(inflation_history.set_index("Year"))

st.write("Unemployment Over Time")
st.line_chart(unemployment_history.set_index("Year"))





    
