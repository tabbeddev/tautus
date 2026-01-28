import re
import typing
from colorama import Fore, Style

regex_email = r"^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$"


def ask_value(
    question: str,
    default: str,
    validationFunction: list[typing.Callable[[str], bool]],
    acceptDefault: bool = False,
    declineMsg: str = "Your answer wans't accepted. Please try correcting your answer",
) -> str:
    while True:
        answer = input(
            f"{Fore.BLUE}{Style.BRIGHT}{question} {Style.RESET_ALL}(e.g. {Fore.GREEN}{default}{Fore.RESET}){Fore.YELLOW} "
        ).strip()

        if answer == "" and acceptDefault:
            return default
        else:
            failed = False
            for function in validationFunction:
                if not function(answer):
                    print(Fore.MAGENTA + declineMsg + Fore.RESET)
                    failed = True
                    break

            if not failed:
                return answer


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
