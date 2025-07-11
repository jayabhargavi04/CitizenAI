# -*- coding: utf-8 -*-
"""CITIZEN AI.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/10XE11HB7RXGmPMdEXaXMVE8BqIsg1zFK
"""

!pip install transformers accelerate gradio

from transformers import AutoTokenizer, AutoModelForCausalLM

HF_TOKEN = "hf_your_actual_token"
model_id = "ibm-granite/granite-3.3-2b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", use_auth_token=HF_TOKEN)

# For causal-conv1d
!pip install causal-conv1d

# For mamba selective state update (only if supported)
!pip install selective-state-update

# Install required libraries
!pip install -q transformers accelerate bitsandbytes gradio

# %%
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os

# Hugging Face Token and Model ID
HF_TOKEN = "hf_your_actual_token"
model_id = "ibm-granite/granite-3.3-2b-instruct"

# Load model and tokenizer from Hugging Face (8-bit mode to save memory)
tokenizer_hub = AutoTokenizer.from_pretrained(model_id, use_auth_token=HF_TOKEN)
model_hub = AutoModelForCausalLM.from_pretrained(
  model_id,
  device_map="auto",
  use_auth_token=HF_TOKEN,
  load_in_8bit=True
)

# Define the local path to save the model
model_path = "/content/granite-model"

# Save the model and tokenizer locally
model_hub.save_pretrained(model_path)
tokenizer_hub.save_pretrained(model_path)

print("Model downloaded and saved locally.")

# %%
# Optional: install causal-conv1d if needed
!pip install -q causal-conv1d

# %%
# Now load model from local path
if not os.path.isdir(model_path):
  print(f"Error: Directory '{model_path}' does not exist.")
elif not os.path.exists(os.path.join(model_path, 'config.json')):
  print(f"Error: '{model_path}' missing 'config.json'.")
elif not os.path.exists(os.path.join(model_path, 'tokenizer_config.json')):
  print(f"Error: '{model_path}' missing 'tokenizer_config.json'.")
else:
  # Load from local path
  tokenizer = AutoTokenizer.from_pretrained(model_path)
  model = AutoModelForCausalLM.from_pretrained(model_path, load_in_8bit=True)

  # Create the pipeline (no device argument!)
  generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

  def generate_response(prompt):
    output = generator(prompt, max_new_tokens=256, do_sample=True, temperature=0.7)
    return output[0]['generated_text']

  print("✅ Model and tokenizer loaded successfully from local path.")

import gradio as gr
import torch

# ✅ Assumes tokenizer, model, and generator are already loaded above this block

def generate_response(prompt):
    output = generator(prompt, max_new_tokens=512, do_sample=False, temperature=0.5)
    return output[0]["generated_text"][len(prompt):].strip()

def handle_feedback(prompt, response, rating, comments):
    print("Prompt:", prompt)
    print("Response:", response)
    print("Rating:", rating)
    print("Comments:", comments)
    return "✅ Thank you for your feedback!"

with gr.Blocks() as demo:
    gr.Markdown("## 🤖 CitizenAI - Ask Public Concerns")
    gr.Markdown("Ask any public safety, legal, or community question.")

    with gr.Row():
        prompt = gr.Textbox(label="Your Question", lines=3, placeholder="What is the procedure to apply for a voter ID?")
        response = gr.Textbox(label="CitizenAI Response", lines=5, interactive=True)

    submit_btn = gr.Button("Get Answer")
    submit_btn.click(fn=generate_response, inputs=prompt, outputs=response)

    gr.Markdown("### 📝 Feedback")
    rating = gr.Radio(["👍 Yes", "👎 No"], label="Was this response helpful?")
    comments = gr.Textbox(label="Comments (optional)", placeholder="Any suggestions or comments?", lines=2)
    feedback_output = gr.Textbox(visible=True, label="Feedback Result", interactive=False)

    submit_feedback = gr.Button("Submit Feedback")
    submit_feedback.click(fn=handle_feedback, inputs=[prompt, response, rating, comments], outputs=feedback_output)

demo.launch(share=True)