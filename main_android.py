
from kivy.app import App
from kivy.uix.webview import WebView
import streamlit.web.bootstrap as bootstrap
import multiprocessing
import os

def run_streamlit():
    bootstrap.run("app.py", "", [], {})

class StatementAnalyzerApp(App):
    def build(self):
        # Start Streamlit server
        process = multiprocessing.Process(target=run_streamlit)
        process.start()
        
        # Create WebView pointing to Streamlit
        webview = WebView(url="http://localhost:8501")
        return webview

if __name__ == '__main__':
    StatementAnalyzerApp().run()
