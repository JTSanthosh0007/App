
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from jnius import autoclass, cast
from android.runnable import run_on_ui_thread
import threading

WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
activity = autoclass('org.kivy.android.PythonActivity').mActivity
LinearLayout = autoclass('android.widget.LinearLayout')
ViewGroup = autoclass('android.view.ViewGroup')

class WebViewApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.webview = None
        Window.softinput_mode = "below_target"
        
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Widget()  # Dummy widget as Kivy requires a widget

    def on_start(self):
        # Start loading the WebView after the Kivy application starts
        Clock.schedule_once(self.create_webview, 0)

    @run_on_ui_thread
    def create_webview(self, *args):
        # Create and configure WebView
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True)
        webview.getSettings().setDatabaseEnabled(True)
        webview.getSettings().setMixedContentMode(0)
        webview.setWebViewClient(WebViewClient())
        
        # Load your hosted Streamlit app URL
        webview.loadUrl('https://your-streamlit-app-url.streamlit.app')
        
        # Add WebView to activity
        layout = LinearLayout(activity)
        layout.setLayoutParams(
            ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        )
        layout.addView(webview)
        activity.setContentView(layout)

if __name__ == '__main__':
    if platform == 'android':
        WebViewApp().run()
