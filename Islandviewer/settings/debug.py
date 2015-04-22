import env


DEBUG = env.DEV_ENV or env.TEST_ENV
TEMPLATE_DEBUG = DEBUG
