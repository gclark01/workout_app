import streamlit as st
from streamlit_option_menu import option_menu

import home, workouts

# if __name__ == '__main__':
#     st.set_page_config(
#         page_title="Coach Adkision Workouts",
#     )

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })
    
    def run():
        with st.sidebar:
            app = option_menu(
                menu_title='Get Big Portal',
                options=['Home', 'Add Workout'],
                icons=['house-fill', 'activity'],
                menu_icon='battery-charging',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "back icon":{"color": "white", "font-size": "23px"}},
                    "nav-link": {"color": "white", "font-size": "12px", "text-nav-selected":{"background-color": "#02AB21"}},
                    "menu-title": {"color": "white", "font-size": "15px"}
                    }
            )
        
        if app == "Home":
            home.app()
        if app == "Add Workout":
            workouts.app()

    
    run()

