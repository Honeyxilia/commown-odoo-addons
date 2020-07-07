{
    "name": "Commown shipping",
    "category": "Business",
    "summary": "Commown shipping-related features",
    "version": "10.0.1.4.0",
    "description": "Commown label printing and shipping followup",
    "author": "Commown SCIC SAS",
    "license": "AGPL-3",
    "website": "https://commown.fr",
    "depends": [
        "sale",
        "website",
        "crm",
        "project",
        "partner_firstname",
    ],
    "external_dependencies": {"bin": ["pdfjam", "pdftk"], },
    "data": [
        "security/ir.model.access.csv",
        "data/parcels.xml",
        "data/actions.xml",
        "views/product.xml",
        "views/project.xml",
        "views/team.xml",
        "views/crm_lead.xml",
    ],
    "demo": ["data/demo.xml", ],
    "installable": True,
}
