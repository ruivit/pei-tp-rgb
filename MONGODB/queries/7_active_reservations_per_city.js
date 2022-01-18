db.atelier.aggregate(
    [{
        $unwind: {
            path: '$reservations'
        }
    }, {
        $match: {
            'reservations.state': 'Active'
        }
        }, {
            $addFields: {
                city: {
                    $concat: [
                        '$reservations.family.origin.cityName',
                        ", ",
                        '$reservations.family.origin.countryName'
                    ]
                }
            }
        }, {
            $group: {
                "_id": '$city',
                "number_of_active_reservations": { "$sum": 1 }
            }
        }, {
            $project: {
                _id: 0,
                city: '$_id',
                number_of_active_reservations: 1,
            }
        }]
).pretty()
