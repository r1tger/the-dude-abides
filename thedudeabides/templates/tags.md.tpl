---
title: "Tags"
date: "{{ date }}"
---

{% for k, v in notes %}

## {{ k }}

{% for b, note in v %}
* {{ note|format_note(b) }}
{% endfor %}
{% endfor %}
