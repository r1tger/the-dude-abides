{{ contents }}
{% if notes_to|length > 0 %}
## Referenties

{% for b, note in notes_to %}
{{ loop.index }}. {{ note|format_note(b, exit_notes) }}
{% endfor %}

{% endif %}

{% if lattices_to|length > 0 %}
## Waar ga je heen?

{% for b, note, paths in lattices_to %}
{{ loop.index }}. {{ note|format_note(b, exit_notes) }}
{% for path in paths %}
[[{{ loop.index }}](?note={{ path|join('&amp;note=') }})]{% if not loop.last %}, {% endif %}

{% endfor %}
{% endfor %}

{% endif %}

{% if lattices_from|length > 0 %}
## Waar kom je vandaan?

{% for b, note, paths in lattices_from %}
{{ loop.index }}. {{ note|format_note(b, exit_notes) }}
{% for path in paths %}
[[{{ loop.index }}](?note={{ path|join('&amp;note=') }})]{% if not loop.last %}, {% endif %}

{% endfor %}
{% endfor %}

{% endif %}
