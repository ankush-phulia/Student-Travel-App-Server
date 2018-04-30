from __future__ import print_function

x = """
{
        "checkpoints": [
            {
                "location": {
                    "location_name": "IIT Delhi",
                    "latitude": "",
                    "longitude": "",
                    "location_type": "Journey Point",
                    "rating": "2.5"
                },
                "transport": "Bus",
                "point_id": "0"
            }
        ],
        "participants": [
            {
                "id": 2,
                "username": "ankush@gmail.com",
                "first_name": "",
                "last_name": "",
                "email": ""
            }
        ],
        "start_time": "2018-05-03T20:00:48Z",
        "source": "IIT Delhi",
        "destination": "Sarai Rohillla",
        "journey_id": "Winter_Vacations"
    },
    {
        "checkpoints": [],
        "participants": [],
        "start_time": "2018-05-03T20:00:48Z",
        "source": "IIT Delhi",
        "destination": "IIT Delhi",
        "journey_id": "Winter_Vacations"
    }"""
def convert(x):
    y = x.replace("\n","").replace(" ","")
    print(y)

convert(x)
