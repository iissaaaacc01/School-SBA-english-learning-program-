#vs code
#python
#activate virtual environment (venv) > python3 -m venv .venv
#                                      source .venv/bin/activate
#pip install flet (install flet library)
import flet as ft
from flet import TextField, Checkbox, ElevatedButton, Column, Row, Text, ControlEvent

# make a page for login
def main(page: ft.Page):
    page.title = "Sign In"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 430
    page.window_resizable = False

    text_username = TextField(label="Username", width=250)
    text_password = TextField(label="Password", width=250, password=True)
    checkbox_signup = Checkbox(label="Done", value=False)
    button_submit = ElevatedButton(text="Sign in", width=250, disabled=True)
    status = Text("", color=ft.colors.GREEN)

    def update_button_state(e: ControlEvent):
        button_submit.disabled = not (text_username.value and text_password.value and checkbox_signup.value)
        page.update()

    def on_submit(e: ControlEvent):
        if button_submit.disabled:
            status.value = "Please fill all fields and check Done."
            status.color = ft.colors.RED
        else:
            status.value = f"Login successful: {text_username.value}"
            status.color = ft.colors.GREEN
        page.update()

    text_username.on_change = update_button_state
    text_password.on_change = update_button_state
    checkbox_signup.on_change = update_button_state
    button_submit.on_click = on_submit

    page.add(
        Column(
            [
                Text("Login", size=24, weight="bold"),
                text_username,
                text_password,
                checkbox_signup,
                button_submit,
                status,
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
