import json
import datetime
import farmService

farm = farmService.myFarm()

input = {
    "area": [
        {
            "id": "269",
            "name": "2020/R/RAW/2025",
            "resource": "taxonomy_term",
            "uri": "https://rothamstedfarm.farmos.net/taxonomy_term/269"
        }
    ],
    "asset": [
        {
            "id": "113",
            "resource": "farm_asset",
            "uri": "https://rothamstedfarm.farmos.net/farm_asset/113"
        }
    ],
    "changed": "1569582240",
    "created": "1569578440",
    "done": "1",
    "equipment": [],
    "files": [],
    "flags": [
        "review"
    ],
    "geofield": [],
    "images": [],
    "input_purpose": "Treatment application",
    "inventory": [],
    "log_category": [
        {
            "id": "273",
            "name": "Treatment",
            "resource": "taxonomy_term",
            "uri": "https://rothamstedfarm.farmos.net/taxonomy_term/273"
        }
    ],
    "log_owner": [
        {
            "id": "16",
            "resource": "user",
            "uri": "https://rothamstedfarm.farmos.net/user/16"
        }
    ],
    "material": [
        {
            "id": 274,
            "name": "Straw",
            "resource": "taxonomy_term",
            "uri": "https://rothamstedfarm.farmos.net/taxonomy_term/274"
        }
    ],
    "name": "Spread treatments for 2020/R/RAW/2025",
    "notes": {
        "format": "farm_format",
        "value": "<p>Broadcast Treatment F wheat by hand before drilling</p>\n"
    },
    "quantity": [],
    "timestamp": "1566169200",
    "type": "farm_input",
    "uid": {
        "id": "17",
        "resource": "user",
        "uri": "https://rothamstedfarm.farmos.net/user/17"
    }
}

farm.log.send(input)