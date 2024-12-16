def migrate(cr, version):
    if not version:
        return
    query = """
update ir_model_fields
set field_description = jsonb_set(
    field_description,
    '{nl_BE}',
    '"Gewicht per Stuk"'
)
where name = 'xx_weight'
and model = 'mrp.production';"""
    cr.execute(query)
