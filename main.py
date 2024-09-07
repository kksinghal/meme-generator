import streamlit as st
from utils import *
from llm import LLM
from threading import Thread

# dataset path
meme_template_path = "Memes templates"

# input fields
st.text_input("Topic/idea...", key="meme_context")
k = st.slider('Number of memes', max_value=10, value=2, key="k")
safety_rating = st.slider('Safety rating, 0 - lowest safety, 3 - high safety filter', min_value=0, max_value=3, value=0, key="safety_rating")

st.button("Re-/Generate", key="generate")

llm = LLM(1, "models/gemini-1.5-pro")

if "n_cols" not in st.session_state: st.session_state["n_cols"] = 3
if "img_paths" not in st.session_state or len(st.session_state["img_paths"]) != k: st.session_state["img_paths"] = [""] * k
if "img_captions" not in st.session_state or len(st.session_state["img_captions"]) != k: st.session_state["img_captions"] = ["Loading..."] * k


# call llm's api and save the response in the global img_caption variable
def generate_caption(img_path, idx, meme_context, img_captions):
    response = llm.generate(f"""
            Generate a witty, high-quality meme-text to be shown below the given meme template. Here's the context we want: {meme_context}. Feel free and be creative. If you find the context or meme template unsafe, just return '****' 
        """, img_path, safety_rating)
    img_captions[idx] = response


# call generate_caption in a thread
def call_generate_caption(img_path, idx, meme_context):
    t = Thread(target=generate_caption, args=[img_path, idx, meme_context, st.session_state["img_captions"]])
    t.start()
    return t


# generate caption for each meme-template in parallel threads
def generate_memes(meme_context):
    meme_text, meme_ext = get_similar_meme_templates(meme_context, st.session_state["k"])
    threads = []
    for idx, (name, ext) in enumerate(zip(meme_text, meme_ext)):
        st.session_state["img_paths"][idx] = os.path.join(meme_template_path, f"{name}.{ext}")
        threads.append(call_generate_caption(st.session_state["img_paths"][idx], idx, meme_context))
    
    for t in threads: t.join()
    return meme_text, meme_ext


# display meme image and caption
if st.session_state["meme_context"] != "":
    meme_text, meme_ext = generate_memes(st.session_state["meme_context"])

    for idx, (name, ext) in enumerate(zip(meme_text, meme_ext)):
        if idx % st.session_state.n_cols == 0:
            cols = st.columns(st.session_state["n_cols"])

        if st.session_state["img_captions"][idx][:4] == "****": 
            st.session_state["img_captions"][idx] = "Some of the contents have been hidden due to safety concerns"
        else:
            st.session_state.img_paths[idx] = os.path.join(meme_template_path, f"{name}.{ext}")
            cols[idx%st.session_state["n_cols"]].image(st.session_state["img_paths"][idx])

        caption_html =f"""
        <div style="background-color:#f0f0f0; padding:10px; margin-bottom: 10px; border-radius:5px; width:100%;">
            <p style="color:#333333; font-size:16px;">{st.session_state["img_captions"][idx]}</p>
        </div>
        """
        cols[idx%st.session_state["n_cols"]].markdown(caption_html, unsafe_allow_html=True)