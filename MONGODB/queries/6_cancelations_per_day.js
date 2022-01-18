db.atelier.aggregate(
    [{
        $unwind: {
            path: '$reservations'
        }
    }, {
        $match: {
            'reservations.state': 'Canceled'
        }
        }, {
            $group: {
                _id: '$date',
                active_reservations: { $first: '$active_reservations' },
                canceled_reservations: { $first: '$canceled_reservations' },
            }
        }, {
            $project: {
                _id: 0,
                date: '$_id',
                active_reservations: 1,
                canceled_reservations: 1,
                reservation_canceled_percentage: {
                    $concat: [
                        {
                            $toString: {
                                $multiply: [
                                    {
                                        $divide: [
                                            '$canceled_reservations',
                                            { $add: ['$active_reservations', '$canceled_reservations'] }
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
