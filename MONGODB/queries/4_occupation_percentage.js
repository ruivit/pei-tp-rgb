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
            $group: {
                _id: '$date',
                active_reservations: { $first: '$active_reservations' }
            }
        }, {
            $project: {
                _id: 0,
                date: '$_id',
                active_reservations: 1,
                occupation_percentage: {
                    $concat: [
                        {
                            $toString: {
                                $multiply: [
                                    {
                                        $divide: [
                                            '$active_reservations',
                                            50
                                        ]
                                    },
                                    100
                                ]
                            }
                        },
                        '%'
                    ]
                }
            }
        }]
).pretty()
