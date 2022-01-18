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
                country: '$reservations.family.origin.countryName'
            }
        }, {
            $group: {
                "_id": '$country',
                "number_of_active_reservations": { "$sum": 1 }
            }
        }, {
            $project: {
                _id: 0,
                country: '$_id',
                number_of_active_reservations: 1,
            }
        }]
).pretty()
