import re
import typing

from tautus.cli.colors import Fore, Style

regex_email = r"^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$"

type ValidationFunctions = list[typing.Callable[[str], bool]]


def confirm(question: str, default: typing.Literal["Y", "N"] | None = None) -> bool:
    default_msg = ""

    if default:
        default_msg = f" {Style.RESET_ALL}(default: {Fore.GREEN}{default}{Fore.RESET})"

    while True:
        answer = input(
            f"{Fore.BLUE}{Style.BRIGHT}{question}{default_msg}{Style.RESET_ALL}{Fore.YELLOW}: "
        )
        answer = answer.upper().strip()

        if answer == "":
            answer = default

        if answer in ["Y", "N"]:
            return answer == "Y"


def validate(input: str, validationFunctions: ValidationFunctions) -> bool:
    for function in validationFunctions:
        if not function(input):
            return False

    return True


def ask_value(
    question: str,
    default: str,
    validationFunctions: ValidationFunctions,
    acceptDefault: bool = False,
    declineMsg: str = "Your answer wasn't accepted. Please try correcting your answer",
) -> str:
    while True:
        answer = input(
            f"{Fore.BLUE}{Style.BRIGHT}{question} {Style.RESET_ALL}(e.g. {Fore.GREEN}{default}{Fore.RESET}){Fore.YELLOW} "
        ).strip()

        if answer == "" and acceptDefault:
            return default
        elif validate(answer, validationFunctions):
            return answer
        else:
            print(Fore.MAGENTA + declineMsg + Fore.RESET)


def v_any(answer: str):
    return True


def v_not_empty(answer: str):
    return len(answer) > 0


def v_lowercase(answer: str):
    return answer.islower()


def v_alphanumeric(answer: str):
    return answer.isalnum()


def v_word(answer: str):
    return answer.replace(" ", "").isalnum()


def v_isemail(answer: str):
    match = re.match(regex_email, answer)
    return match != None


vp_name = [v_not_empty, v_lowercase, v_alphanumeric]
vp_title = [v_not_empty, v_word]
vp_description = [v_not_empty]
vp_maintainer_name = [v_not_empty]
vp_email = [v_isemail]
