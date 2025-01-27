import gradio as gr
import requests

# Define the function to interact with the Ollama API
def process_image_and_question(image_path, question):
    try:
        # Ensure an image and question are provided
        if not image_path:
            return "Error: Please upload an image."
        if not question.strip():
            return "Error: Please enter a question."

        # Read the image file as bytes
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        # Prepare the payload
        payload = {"question": question}
        files = {"image": ("uploaded_image.jpeg", image_bytes, "image/jpeg")}

        # Make the request to the Ollama LLaVA API
        response = requests.post(
            "http://localhost:11434/api/ask",  # Ollama API endpoint
            files=files,
            data=payload
        )

        # Check the response
        if response.status_code == 200:
            return response.json().get("response", "No response generated.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("### Analyze Images Using Ollama's LLaVA")

    with gr.Row():
        image_input = gr.Image(type="filepath", label="Upload JPEG Image")
        question_input = gr.Textbox(label="Ask a Question About the Image")

    answer_output = gr.Textbox(label="Answer", interactive=False)

    analyze_button = gr.Button("Analyze Image")
    analyze_button.click(process_image_and_question, inputs=[image_input, question_input], outputs=[answer_output])

app.launch(server_name="0.0.0.0", server_port=7864)
