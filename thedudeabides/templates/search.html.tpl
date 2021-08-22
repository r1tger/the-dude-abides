<form>
    <fieldset>
        <input type="text" placeholder="Zoeken" id="search"/>
    </fieldset>
</form>
<table>
    <thead>
        <tr>
            <th style="text-align: left;">Term</th>
            <th style="text-align: left;">Notities</th>
        </tr>
    </thead>
    <tbody id="tokens">
    {% for token, notes in inverted_index.items()|sort %}
        <tr style="display: none;" id="{{ token }}">
            <td>{{ token }}</td>
            <td>{% for n in notes|sort %}<a href="{{ n.get_id()}}.html" title="{{ n.get_title() }}">{{ n.get_id()}}</a>{% if not loop.last %}, {% endif %}{% endfor %}</td>
        </tr>
    {% endfor %}
    </tbody>
</table>
