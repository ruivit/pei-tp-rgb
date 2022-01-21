db.atelier.aggregate(
[{$unwind: {
    path: '$reservations'
    }}, {$match: {
    'reservations.state': 'Canceled'
    }}, {$group: {
    _id: '$date',
    peopleInCanceledReservations: {
        $sum: '$reservations.family.numberElements'
    }
    }}, {$addFields: {
    people_in_canceled_reservations: '$peopleInCanceledReservations'
    }}, {}]
).pretty()