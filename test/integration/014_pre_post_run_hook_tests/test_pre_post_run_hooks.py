from test.integration.base import DBTIntegrationTest


RUN_HOOK_TEMPLATE = """
   insert into pre_post_run_hooks_014.on_run_hook (
        "state",
        "target.dbname",
        "target.host",
        "target.name",
        "target.schema",
        "target.type",
        "target.user",
        "target.pass",
        "target.port",
        "target.threads",
        "run_started_at",
        "invocation_id"
   ) VALUES (
    '{{ state }}',
    '{{ target.dbname }}',
    '{{ target.host }}',
    '{{ target.name }}',
    '{{ target.schema }}',
    '{{ target.type }}',
    '{{ target.user }}',
    '{{ target.pass }}',
    {{ target.port }},
    {{ target.threads }},
    '{{ run_started_at }}',
    '{{ invocation_id }}'
   )
"""

RUN_START_HOOK = RUN_HOOK_TEMPLATE
RUN_END_HOOK = RUN_HOOK_TEMPLATE

class TestPrePostRunHooks(DBTIntegrationTest):

    def setUp(self):
        DBTIntegrationTest.setUp(self)

        self.run_sql_file("test/integration/014_pre_post_run_hook_tests/seed.sql")

        self.fields = [
            'state',
            'target.dbname',
            'target.host',
            'target.name',
            'target.port',
            'target.schema',
            'target.threads',
            'target.type',
            'target.user',
            'target.pass',
            'run_started_at',
            'invocation_id'
        ]

    @property
    def schema(self):
        return "pre_post_run_hooks_014"

    @property
    def project_config(self):
        return {
            "on-run-start": RUN_START_HOOK,
            "on-run-end":   RUN_END_HOOK
        }

    @property
    def models(self):
        return "test/integration/014_pre_post_run_hook_tests/models"

    def get_ctx_vars(self, state):
        field_list = ", ".join(['"{}"'.format(f) for f in self.fields])
        query = "select {field_list} from {schema}.on_run_hook where state = '{state}'".format(field_list=field_list, schema=self.schema, state=state)

        vals = self.run_sql(query)
        self.assertFalse(len(vals) == 0, 'nothing inserted into on_run_hook table')
        ctx = dict([(k,v) for (k,v) in zip(self.fields, vals[0])])

        return ctx

    def test_pre_post_run_hooks(self):
        self.run_dbt(['run'])

        ctx = self.get_ctx_vars('start')

        self.assertEqual(ctx['state'], 'start')
        self.assertEqual(ctx['target.dbname'], 'dbt')
        self.assertEqual(ctx['target.host'], 'database')
        self.assertEqual(ctx['target.name'], 'default2')
        self.assertEqual(ctx['target.port'], 5432)
        self.assertEqual(ctx['target.schema'], 'pre_post_run_hooks_014')
        self.assertEqual(ctx['target.threads'], 1)
        self.assertEqual(ctx['target.type'], 'postgres')
        self.assertEqual(ctx['target.user'], 'root')
        self.assertEqual(ctx['target.pass'], '')

        self.assertTrue(ctx['run_started_at'] is not None and len(ctx['run_started_at']) > 0, 'run_started_at was not set')
        self.assertTrue(ctx['invocation_id'] is not None and len(ctx['invocation_id']) > 0, 'invocation_id was not set')

