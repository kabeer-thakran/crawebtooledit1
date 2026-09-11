"""Word-report rendering package for the CRA tool.

``prepare_template`` is a one-time developer script that converts the Arup
``[Placeholder]`` Word template into a Jinja2 ``docxtpl`` template;
``docx_renderer`` turns a filled :class:`~core.schema.CRAReport` into the final
``.docx`` bytes.
"""
