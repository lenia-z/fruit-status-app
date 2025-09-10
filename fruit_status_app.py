import os, requests
import streamlit as st
from dotenv import load_dotenv

# Configuration
load_dotenv()
def cfg(name, default=""):
    return os.getenv(name) or st.secrets.get(name, default)
PREDICTION_URL_IMAGE = cfg("PREDICTION_URL_IMAGE")
PREDICTION_URL_URL   = cfg("PREDICTION_URL_URL")
PREDICTION_KEY       = cfg("PREDICTION_KEY")

# UI
st.set_page_config(page_title="Fruit Status Classifier", layout="centered")
st.title("Fresh vs Rotten Fruit \n🍎🍊🍌🍉🍇🍓🍒🍍🥭🥝")

tab_upload, tab_url = st.tabs(["Upload Image", "Image URL"])

# Prediction functions
# Predict from image bytes
def predict_bytes(img_bytes: bytes):
    if not PREDICTION_URL_IMAGE:
        st.error("The PREDICTION_URL_IMAGE environment variable is not set!")
        return None
    
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }

    r = requests.post(PREDICTION_URL_IMAGE, headers=headers, data=img_bytes, timeout=30)
    if not r.ok:
        st.error(f"Request failed: {r.status_code} - {r.text}")
        return None
    return r.json()

# Predict from image URL
def predict_url(img_url: str):
    if not PREDICTION_URL_URL:
        st.error("The PREDICTION_URL_URL environment variable is not set!")
        return None
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/json"
    }

    payload = {"Url": img_url}

    r = requests.post(PREDICTION_URL_URL, headers=headers, json=payload, timeout=30)
    if not r.ok:
        st.error(f"Request failed: {r.status_code} - {r.text}")
        return None
    return r.json()

def show_result(resp_json):
    # Parse predictions
    preds = resp_json.get("predictions")

    if not preds:
        st.warning("Sorry, no predictions were returned.")
        return
    
    top = max(preds, key=lambda x: x.get("probability", 0.0))

    # Display results
    st.success(f"Result: {top['tagName']}  |  Confidence: {top['probability']:.2%}")
    st.caption("Full predictions:")
    st.table([{"tag": p["tagName"], "prob": f"{p['probability']:.2%}"} for p in preds])

with tab_upload:
    file = st.file_uploader("Please upload an image file:", type=["jpg", "jpeg", "png"])

    clicked_upload = st.button("Try it! 👀", key="btn_upload", disabled=not bool(file))
    if clicked_upload:
        st.image(file, caption="Uploaded Image", width='stretch')
        resp = predict_bytes(file.read())
        show_result(resp)

with tab_url:
    url = st.text_input("Please enter an image url:", placeholder="https://example.com/your-image.jpg")

    clicked_url = st.button("Try it! 👀", key="btn_url", disabled=not bool(url))
    if clicked_url:
        st.image(url, caption="Image from URL", width='stretch')
        resp = predict_url(url)
        show_result(resp)
