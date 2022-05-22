
class NetmikoConnectionError(RuntimeError):
    ROBOT_SUPPRESS_NAME = True
    ROBOT_EXIT_ON_FAILURE = True


class NetmikoError(RuntimeError):
    ROBOT_SUPPRESS_NAME = True


class NetmikoTimeout(RuntimeError):
    ROBOT_SUPPRESS_NAME = True


class ParserException(RuntimeError):
    ROBOT_SUPPRESS_NAME = True

    def __init__(self, text, template):
        """Generic exception when processing text using TTP.

        Args:
            text (str)
            template (str)
        """
        self.text = text
        self.template = template

    def __str__(self):
        msg = ''.join(("Unable to parse text using the provided template.",
                       f"Text:\n{self.text}\n\n",
                       "Tried to parse text using:\n\n",
                       f"{self.template}"
                       "Please validate the CLI command is returning the"
                       "correct text and that your template is accurate."))
        return msg
