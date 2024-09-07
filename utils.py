import streamlit as st
from sentence_transformers import SentenceTransformer
import os
import numpy as np
# import matplotlib.pyplot as plt
import pickle

# dataset path
meme_template_path = "Memes templates"


@st.cache_resource
def get_sentence_transformer():
    return SentenceTransformer("all-mpnet-base-v2")


# return text descriptions (name of each template file) and their extensions (.jpg, .png)
@st.cache_data
def get_meme_template_names():
    files = os.listdir(meme_template_path)
    return [name[:-4] for name in files], [name[-3:] for name in files]


# return k-nearest templates to given context
def get_similar_meme_templates(context, k):
    model = get_sentence_transformer()
    meme_text, img_extension = get_meme_template_names()
    if not os.path.exists("./meme_templates_embeddings.pickle"):
        meme_text_embedding = model.encode(meme_text)
        with open('./meme_templates_embeddings.pickle', 'wb') as handle: pickle.dump(meme_text_embedding, handle)
    else:
        with open('./meme_templates_embeddings.pickle', 'rb') as handle: meme_text_embedding = pickle.load(handle)

    context_embedding = model.encode(context)
    similarities = (model.similarity(meme_text_embedding, context_embedding).squeeze().numpy()-1+1e-10)/2
    
    ##### for probabilistic sampling #####
    # probs = (1/similarities) / np.sum(1/similarities)
    # probs = np.power(1000, similarities) / np.sum(np.power(1000, similarities))
    # ind = np.random.choice(np.arange(len(probs)), k, replace=False, p=probs)

    
    ##### for displaying the probabilty distribution #####
    # Visualise the prob distribution
    # n_bins = 20
    # fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
    # # We can set the number of bins with the *bins* keyword argument.
    # axs[0].hist(probs, bins=n_bins)
    # st.pyplot(fig)

    ind = np.argpartition(similarities, -k)[-k:] # top-k
    ind = ind[np.argsort(similarities[ind])]
    return np.array(meme_text, dtype=object)[ind], np.array(img_extension)[ind]
