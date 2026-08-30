# Data Fusion Skill

Never merge by silent overwrite.

Maintain an evidence table:
entity_id
source
attribute
value
timestamp
geometry
quality
status

When values disagree, emit CONFLICT and preserve all sources.

Fusion may produce a derived value only when the rule/model is documented.
