from web.models.result import Result
from jinja2 import Template
import itertools
import html
name = "Hex dump"

def html_pad(string: str, total_len: int) -> str:
    ...

def hex_diff(gold: bytes, user: bytes) -> str:
    bytes_to_compare = itertools.zip_longest(gold, user)
    ret_str = ""
    gold_hex = gold_str = user_hex = user_str = ""
    gold_len = user_len = 0
    for index, byte_pair in enumerate(bytes_to_compare):
        if byte_pair[0] == byte_pair[1]:
            gold_hex += "{:02x} ".format(byte_pair[0])
            user_hex += "{:02x} ".format(byte_pair[1])
            gold_str += html.escape(chr(byte_pair[0])) if 32 <= byte_pair[0] < 128 else '<span style="color:gray;">.</span>'
            user_str += html.escape(chr(byte_pair[1])) if 32 <= byte_pair[1] < 128 else '<span style="color:gray;">.</span>'
            gold_len += 1
            user_len += 1
        else:
            if byte_pair[0] is not None:
                gold_hex += f'<span style="background-color:#FFFF99;">{byte_pair[0]:02x}</span> '
                gold_char = html.escape(chr(byte_pair[0])) if 32 <= byte_pair[0] < 128 else '<span style="color:gray;">.</span>'
                gold_str += f'<span style="background-color:#FFFF99;">{gold_char}</span>'
                gold_len += 1
            if byte_pair[1] is not None:
                user_hex += f'<span style="background-color:#FFFF99;">{byte_pair[1]:02x}</span> '
                user_char = html.escape(chr(byte_pair[1])) if 32 <= byte_pair[1] < 128 else '<span style="color:gray;">.</span>'
                user_str += f'<span style="background-color:#FFFF99;">{user_char}</span>'
                user_len += 1

        if index % 8 == 7:
            ret_str += f"0x{index-7:08x}  {gold_hex}{' '*3*(8-gold_len)}  {gold_str}{' '*(8-gold_len)} | {user_hex}{' '*3*(8-user_len)}  {user_str}{' '*(8-user_len)}\n"
            gold_hex = gold_str = user_hex = user_str = ""
            gold_len = user_len = 0
        
    if gold_hex != "":  # We didn't end up with an even row:
        ret_str += f"0x{(len(list(bytes_to_compare)) // 8) * 8:08x}  {gold_hex}{' '*3*(8-gold_len)}  {gold_str}{' '*(8-gold_len)} | {user_hex}{' '*3*(8-user_len)}  {user_str}{' '*(8-user_len)}\n"

    return ret_str

def format_output(result: Result) -> str:
    return Template("""
    <table class="table">
        <tr>
            <td><!-- label --></td>
            <th>Gold</th>
            <th>You</th>
        </tr>
        {% if not result.stdout_correct %}
        <tr>
            <th>Standard output:</th>
            <td colspan="2">
                <pre>{{ stdout }}</pre>
            </td>
        </tr>
        {% endif %}
        {% if not result.stderr_correct %}
        <tr>
            <th>Standard error:</th>
            <td colspan="2">
                <pre>{{ stderr }}</pre>
            </td>
        </tr>
        {% endif %}
        {% if not result.return_code_correct %}
        <tr>
            <th>Return code:</th>
            <td>
                <pre>{{ result.correct_result.return_code }}</pre>
            </td>
            <td>
                <pre>{{ result.return_code }}</pre>
            </td>
        </tr>
        {% endif %}
    </table>
""").render(
        result=result,
        stdout=hex_diff(result.correct_result.stdout, result.stdout),
        stderr=hex_diff(result.correct_result.stderr, result.stderr)
    )
