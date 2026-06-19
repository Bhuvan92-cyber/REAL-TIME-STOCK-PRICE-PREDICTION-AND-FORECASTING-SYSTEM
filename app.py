import gradio as gr
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# 1. Import your local modules and models
# (Replace these with the actual functions from your repo)
# ---------------------------------------------------------
# Example: from src.preprocessing import process_data
# Example: from src.models import build_transformer

def load_models():
    """
    Load the pre-trained weights for the architecture.
    Ensure your model weights (.h5, .pt, .pkl) are in the repository.
    """
    print("Loading CNN, Bi-GRU, and Transformer models...")
    # cnn_model = load_model('models/cnn_weights.h5')
    # bigru_model = load_model('models/bigru_weights.h5')
    # transformer_model = load_model('models/transformer_weights.h5')
    
    # Return a dictionary or tuple of your loaded models
    return {"cnn": None, "bigru": None, "transformer": None}

# Initialize models globally so they only load once when the Space starts
models = load_models()

# ---------------------------------------------------------
# 2. Define the Prediction Logic
# ---------------------------------------------------------
def forecast_stock(ticker, days_to_predict):
    """
    Fetches real-time data, runs inference, and generates a plot.
    """
    try:
        # Fetch real-time data
        stock_data = yf.download(ticker, period="1y")
        if stock_data.empty:
            return None, f"Error: Could not fetch data for ticker '{ticker}'."

        # --- INSERT YOUR PREPROCESSING AND INFERENCE HERE ---
        # 1. Preprocess stock_data (scaling, creating sequences)
        # 2. Pass sequences to models['cnn'], models['bigru'], models['transformer']
        # 3. Ensemble the predictions
        # ----------------------------------------------------
        
        # MOCK DATA FOR VISUALIZATION (Replace with actual model output)
        historical_prices = stock_data['Close'].values[-60:]
        future_dates = pd.date_range(start=stock_data.index[-1], periods=days_to_predict + 1)[1:]
        mock_predictions = [historical_prices[-1] * (1 + np.random.normal(0, 0.02)) for _ in range(days_to_predict)]

        # ---------------------------------------------------------
        # 3. Generate the Output Graph
        # ---------------------------------------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Plot historical
        ax.plot(range(60), historical_prices, label="Historical (Last 60 Days)", color="blue")
        
        # Plot forecast
        forecast_x = range(59, 59 + days_to_predict + 1)
        forecast_y = [historical_prices[-1]] + mock_predictions
        ax.plot(forecast_x, forecast_y, label="Forecasted Trend", color="orange", linestyle="--")
        
        ax.set_title(f"{ticker} Real-Time Forecast")
        ax.set_xlabel("Days")
        ax.set_ylabel("Price")
        ax.legend()
        
        # Return the plot and a status message
        return fig, f"Successfully generated a {days_to_predict}-day forecast for {ticker}."
        
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

# ---------------------------------------------------------
# 4. Build the Gradio Web Interface
# ---------------------------------------------------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Real-Time Stock Price Prediction System")
    gr.Markdown("Powered by an ensemble of CNN, Bi-GRU, and Transformer models.")
    
    with gr.Row():
        with gr.Column(scale=1):
            ticker_input = gr.Textbox(label="Stock Ticker (e.g., AAPL, TSLA, INFY.NS)", value="AAPL")
            days_input = gr.Slider(minimum=1, maximum=30, step=1, value=7, label="Days to Forecast")
            submit_btn = gr.Button("Generate Forecast", variant="primary")
            
        with gr.Column(scale=2):
            output_plot = gr.Plot(label="Price Projection")
            output_text = gr.Textbox(label="System Status", interactive=False)
            
    # Link the inputs to the inference function
    submit_btn.click(
        fn=forecast_stock,
        inputs=[ticker_input, days_input],
        outputs=[output_plot, output_text]
    )

# ---------------------------------------------------------
# 5. Launch the App
# ---------------------------------------------------------
if __name__ == "__main__":
    demo.launch()