# Bits

All bits that inhabit the theory:

{% assign bits = site.pages | where_exp: "page", "page.path contains 'terms/bits/'" | where_exp: "page", "page.name != 'index.md'" %}
{% for bit in bits %}
- [{{ bit.name | remove: '.md' | replace: '_', ' ' | capitalize }}]({{ bit.url | relative_url }})
{% endfor %}