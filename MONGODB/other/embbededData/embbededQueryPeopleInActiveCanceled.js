db.atelier.aggregate(
[{$unwind: {
    path: '$reservations'
   }}, {$match: {
    'reservations.state': 'Active'
   }}, {$group: {
    _id: '$date',
    peopleInActiveReservations: {
     $sum: '$reservations.family.numberElements'
    }
   }}, {$addFields: {
    people_in_active_reservations: '$peopleInCanceledReservations'
   }}, {}]
).pretty()

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