# octowalrus service Tiltfile
# This can be run independently or included by the main manifests Tiltfile
load('ext://secret', 'secret_from_dict')
load('ext://configmap', 'configmap_from_dict')
load('ext://dotenv', 'dotenv')

# CONFIGURATION
allow_k8s_contexts('docker-desktop')
dotenv()  # enriches os.environ with .env vars

# CONSTANTS
SYSENV = dict(os.environ)

# FUNCTIONS: we should move these to their own repo https://docs.tilt.dev/extensions.html#managing-your-own-extension-repo
def safe_local(cmd, default=''):
    """Execute a local command, return default value if it fails"""
    return str(local(cmd + ' 2>/dev/null || echo "' + default + '"')).strip() or default

def get_env_var(key, default=""):
    """Get environment variable with priority: system env > other secrets > default"""
    if key in SYSENV:
        return SYSENV[key]
    return default

# SECRETS/CONFIGMAPS
k8s_yaml(
    configmap_from_dict(
        'octowalrus-config', 
        inputs={
            'APP_ENV': get_env_var('APP_ENV', 'development'),
            'CORS_ALLOW_URLS': get_env_var('CORS_ALLOW_URLS', 'http://localhost:17300,http://127.0.0.1:17300,http://localhost:17600,http://127.0.0.1:17600'),
            'DEBUGPY_ENABLED': get_env_var('DEBUGPY_ENABLED', 'true'),
            'DEBUGPY_WAIT': get_env_var('DEBUGPY_WAIT', 'false'),
            'DEBUGPY_PORT': get_env_var('DEBUGPY_PORT', '5678'),
            'INSTALL_DEV_DEPS': get_env_var('INSTALL_DEV_DEPS', 'true'),
        }
    )
)

# MANIFESTS
k8s_yaml(helm(
    'manifests',
    values=['manifests/values-dev.yaml']
))

# BUILDS
docker_build(
    'octowalrus-app',
    context='.',
    dockerfile='Dockerfile',
    build_args={
        'INSTALL_DEV_DEPS': get_env_var("INSTALL_DEV_DEPS", "true"),
    },
    live_update=[
        fall_back_on(['./.env']),
        sync('./src/', '/app/src/'),
        sync('./pyproject.toml', '/app/pyproject.toml'),
    ],
)

# RESOURCES
k8s_resource(
    'octowalrus',
    port_forwards=[
        # HOST:PORT, CONTAINER:PORT
        port_forward(18080, 8000, name="octowalrus-api"),
        port_forward(18085, 5678, name="octowalrus-debug"),
    ],
    resource_deps=[],
    labels=['backend'],
    links=[
        link('http://localhost:18080/docs', 'Swagger UI'),
        link('http://localhost:18080/redoc', 'ReDoc'),
        link('http://localhost:18080/openapi.json', 'OpenAPI JSON'),
    ],
)