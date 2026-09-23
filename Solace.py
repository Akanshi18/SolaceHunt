import streamlit as st
from groq import Groq

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="SOLACE - Rental Assistant",
    page_icon="🏠",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f7fafc;
}

.title {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
    color: #2563eb;
}

.subtitle {
    text-align: center;
    color: gray;
    margin-bottom: 2rem;
}

.footer {
    text-align: center;
    color: gray;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_INSTRUCTION = """
Your name is SOLACE.

You are a Rental Property Assistant.

For your FIRST reply in every new conversation,
start your response with:

Meow! 🐾

You can only help users with:

- Flats for rent
- Apartments for rent
- PG accommodations
- Rental homes
- Co-living spaces
- Family rentals
- Bachelor rentals
- Student accommodations
- Rental advice
- Locality comparison
- Property amenities
- Rental agreements
- Budget guidance

If the user asks anything unrelated to rentals,
properties, houses, flats, PGs or accommodation,
reply ONLY:

"Meow! 🐾 I am SOLACE and can only help with rental properties, flats, PGs, accommodation, and rent-related queries."

Always try to collect:

- City
- Locality
- Budget
- Occupancy Type
- Amenities Required

Never invent property listings.

Never claim a property is available unless explicitly provided.

Be helpful, friendly and concise.
"""

# --------------------------------------------------
# API KEY
# --------------------------------------------------

api_key = "AQ.Ab8RN6KPhFZHz6CyOsC3KYYuQpglBMNyS8J_WYHsPCtEBqkEMQ"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "first_response" not in st.session_state:
    st.session_state.first_response = True

# --------------------------------------------------
# CATEGORY DETECTION
# --------------------------------------------------

def detect_category(query):

    query = query.lower()

    if any(word in query for word in [
        "pg",
        "paying guest",
        "hostel",
        "shared room"
    ]):
        return "🏠 PG"

    elif any(word in query for word in [
        "flat",
        "apartment",
        "1bhk",
        "2bhk",
        "3bhk",
        "4bhk"
    ]):
        return "🏢 Flat"

    elif any(word in query for word in [
        "family",
        "kids",
        "parents"
    ]):
        return "👨‍👩‍👧 Family Rental"

    elif any(word in query for word in [
        "student",
        "bachelor",
        "working professional"
    ]):
        return "🎓 Bachelor / Student"

    return "📍 General Rental Query"

# --------------------------------------------------
# RENTAL TIPS
# --------------------------------------------------

tips = [
    "🏠 Visit the property before paying any deposit.",
    "📄 Read the rental agreement carefully.",
    "🔐 Check security arrangements.",
    "🚇 Verify transport connectivity.",
    "💡 Confirm maintenance charges.",
    "📶 Check internet availability.",
    "🚗 Ask about parking facilities.",
    "🧹 Verify cleaning and housekeeping services."
]

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🏠 SOLACE")

    st.write("Your Rental Property Assistant")

    st.markdown("---")

    st.subheader("🔍 Property Preferences")

    city = st.text_input("City")

    locality = st.text_input("Preferred Locality")

    budget = st.number_input(
        "Monthly Budget (₹)",
        min_value=1000,
        value=10000,
        step=1000
    )

    occupancy = st.selectbox(
        "Occupancy Type",
        [
            "Bachelor",
            "Family",
            "Student",
            "Working Professional"
        ]
    )

    amenities = st.multiselect(
        "Preferred Amenities",
        [
            "WiFi",
            "Meals",
            "Parking",
            "AC",
            "Laundry",
            "Security",
            "Gym",
            "Housekeeping"
        ]
    )

    st.markdown("---")

    st.subheader("💡 Rental Tip")

    st.info(random.choice(tips))

    st.markdown("---")

    st.subheader("❓ Suggested Questions")

    st.write("• Looking for a PG in Pune under ₹10,000")
    st.write("• Need a 2 BHK for family in Navi Mumbai")
    st.write("• Best locality for IT professionals?")
    st.write("• Furnished flat for bachelors")
    st.write("• PG with meals and WiFi")

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.first_response = True
        st.rerun()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="title">🏠 SOLACE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Helping You Find Flats, PGs & Rental Homes</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

question_count = len(
    [
        msg
        for msg in st.session_state.messages
        if msg["role"] == "user"
    ]
)

st.metric(
    "Questions Asked",
    question_count
)

# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------------------------
# DOWNLOAD CHAT
# --------------------------------------------------

chat_json = json.dumps(
    st.session_state.messages,
    indent=2
)

st.download_button(
    "📥 Download Chat History",
    data=chat_json,
    file_name="solace_chat.json",
    mime="application/json"
)

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

prompt = st.chat_input(
    "Ask me about PGs, flats, rental homes..."
)

# --------------------------------------------------
# PROCESS MESSAGE
# --------------------------------------------------

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    category = detect_category(prompt)

    st.info(
        f"Category Detected: {category}"
    )

    property_details = f"""
Property Preferences

City: {city}
Locality: {locality}
Budget: ₹{budget}
Occupancy Type: {occupancy}
Amenities: {", ".join(amenities) if amenities else "Not Specified"}

User Question:
{prompt}
"""

    try:

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=property_details,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.5,
                max_output_tokens=800
            )
        )

        answer = response.text

        if st.session_state.first_response:
            answer = "Meow! 🐾 " + answer
            st.session_state.first_response = False

        with st.chat_message("assistant"):

            placeholder = st.empty()
            full_response = ""

            for word in answer.split():

                full_response += word + " "

                placeholder.markdown(
                    full_response
                )

                time.sleep(0.01)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
    🏠 SOLACE | Flats • PGs • Rentals • Property Guidance
    </div>
    """,
    unsafe_allow_html=True
)
