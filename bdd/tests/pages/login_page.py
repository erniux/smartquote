from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.user_input = page.get_by_placeholder("Email")  # ajusta a tu UI
        self.pass_input = page.get_by_placeholder("Password")
        self.submit_btn = page.get_by_role("button", name="Iniciar sesión")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/login")

    def login(self, email: str, password: str):
        self.user_input.fill(email)
        self.pass_input.fill(password)
        self.submit_btn.click()
