import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-open-synergy-akn-hr",
    description="Meta package for open-synergy-akn-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-hr_advance',
        'odoo11-addon-hr_travel_request',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
