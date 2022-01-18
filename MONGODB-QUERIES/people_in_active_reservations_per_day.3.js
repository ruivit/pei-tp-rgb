db.atelier.aggregate(
    [{$unwind: {
        path: '$reservations'
       }}, {$match: {
        'reservations.state': 'Active'
       }}, {$group: {
        _id: '$date',
        people_in_active_reservations: {
         $sum: '$reservations.family.numberElements'
        }
       }}, {$project: {
        _id: 0,
        date: '$_id',
        people_in_active_reservations: 1
       }}]
).pretty()
