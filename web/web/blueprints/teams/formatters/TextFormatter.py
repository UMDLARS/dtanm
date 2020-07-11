from web.models.result import Result
from jinja2 import Template
name = "Plain Text"

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
            <td>
                <pre>{{ result.correct_result.stdout }}</pre>
            </td>
            <td>
                <pre>{{ result.stdout.stdout }}</pre>
            </td>
        </tr>
        {% endif %}
        {% if not result.stderr_correct %}
        <tr>
            <th>Standard error:</th>
            <td>
                <pre>{{ result.correct_result.stderr }}</pre>
            </td>
            <td>
                <pre>{{ result.stderr }}</pre>
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
""").render(result=result)
