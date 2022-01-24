db.atelier.aggregate(
[{$project: {
    _id: 0,
    date: 1,
    slots: 1,
    active_reservations: 1,
    canceled_reservations: 1,
    people_in_active_reservations: 1,
    people_in_canceled_reservations: 1
    }}, {$out: 'atelierdotxml'}]
).pretty()