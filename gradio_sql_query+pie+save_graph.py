import gradio as gr
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import tempfile

# Global DataFrame to store query results
query_result_df = None
temp_image_path = None  # Temporary path for the generated graph

def run_query(db_name, sql_query):
    global query_result_df
    try:
        # Validate database name
        if not db_name.endswith(".db"):
            db_name += ".db"
        
        # Connect to the database
        conn = sqlite3.connect(db_name)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        
        # Ensure the query returns valid data
        if df.empty:
            return "Query returned no results.", None
        
        query_result_df = df  # Store query result for graphing
        return df.to_html(index=False, classes="table"), gr.update(interactive=True)
    except Exception as e:
        return f"Error: {e}", gr.update(interactive=False)

def generate_graph():
    global query_result_df, temp_image_path
    try:
        if query_result_df is None or query_result_df.empty:
            return None, "Error: No query results to graph."
        
        if len(query_result_df.columns) < 2:
            return None, "Error: Query must return at least two columns (e.g., value and count)."
        
        # Clean data to remove None or NaN values
        cleaned_df = query_result_df.dropna().copy()
        
        # Save the cleaned dataframe as a temporary CSV file
        with tempfile.NamedTemporaryFile(delete=False, mode='w', newline='') as temp_csv_file:
            cleaned_df.to_csv(temp_csv_file, index=False)
            temp_csv_file_path = temp_csv_file.name
        
        # Now load the CSV and graph it
        graph_data = pd.read_csv(temp_csv_file_path)

        # Plot a pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(graph_data.iloc[:, 1], labels=graph_data.iloc[:, 0].astype(str), autopct='%1.1f%%', startangle=90, 
                colors=plt.cm.Paired.colors)
        plt.title("Unique Instances and Their Counts", fontsize=16)

        # Save the plot to a temporary PNG file
        temp_image_path = tempfile.mktemp(suffix=".png")
        plt.savefig(temp_image_path)
        plt.close()

        # Clean up the temporary CSV file
        os.remove(temp_csv_file_path)

        # Return the image file path
        return temp_image_path, "Graph generated successfully."
    except Exception as e:
        return None, f"Error: {e}"

def save_graph(file_name):
    global temp_image_path
    try:
        if temp_image_path is None or not os.path.exists(temp_image_path):
            return "Error: No graph available to save."
        
        # Ensure the file name ends with .jpeg
        if not file_name.endswith(".jpeg"):
            file_name += ".jpeg"
        
        # Save the temporary PNG as a JPEG
        jpeg_path = os.path.join(os.getcwd(), file_name)
        with open(temp_image_path, "rb") as temp_image_file:
            with open(jpeg_path, "wb") as jpeg_file:
                jpeg_file.write(temp_image_file.read())
        
        return f"Graph saved as '{file_name}' successfully."
    except Exception as e:
        return f"Error: {e}"

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("### Query a Custom SQLite Database and Visualize Results")
    
    db_name_input = gr.Textbox(label="Database Name (e.g., 'my_database.db')")
    query_input = gr.Textbox(label="Enter SQL Query")
    result_output = gr.HTML(label="Query Result Table")
    graph_output = gr.Image(label="Graph Visualization")
    query_status = gr.Textbox(label="Status", interactive=False)
    file_name_input = gr.Textbox(label="JPEG File Name (e.g., 'graph.jpeg')")
    save_status = gr.Textbox(label="Save Status", interactive=False)
    
    query_button = gr.Button("Run Query")
    graph_button = gr.Button("Generate Graph", interactive=False)
    save_button = gr.Button("Save File")
    
    query_button.click(run_query, 
                       inputs=[db_name_input, query_input], 
                       outputs=[result_output, graph_button])
    
    graph_button.click(generate_graph, 
                       outputs=[graph_output, query_status])
    
    save_button.click(save_graph, 
                      inputs=[file_name_input], 
                      outputs=[save_status])

app.launch(server_name="0.0.0.0", server_port=7863)
