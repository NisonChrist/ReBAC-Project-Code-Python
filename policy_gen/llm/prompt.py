from string import Template


class Prompt:
    def __init__(self, system: str, user: str, template: str):
        self._system_msg = system
        self._user_msg = user
        self.template = Template(template)

    def get_system_msg(self) -> str:
        return self._system_msg

    def get_user_msg(self) -> str:
        return self._user_msg

    def format(self, **kwargs) -> dict[str, str]:
        formatted_user = self.template.substitute(**kwargs)
        return {"system": self._system_msg, "user": formatted_user}

    def __str__(self):
        return f"System Msg: {self._system_msg}\nUser Msg: {self._user_msg}"
